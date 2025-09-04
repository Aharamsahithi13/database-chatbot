import ollama
import re
from functools import lru_cache
from configure import OLLAMA_MODEL

@lru_cache(maxsize=100)
def cached_ollama_response(query: str) -> str:
    response = ollama.chat(
        model=OLLAMA_MODEL,
        messages=[{"role": "user", "content": query}]
    )
    return response["message"]["content"]

def classify_query(query: str) -> str:
    student_keywords = {
        "student", "roll_no", "roll number", "marks", "subject", "name", "age", "gender",
        "address", "enrolled", "computer science", "ds", "cs", "database", "show", "list",
        "count", "how many", "number of", "department", "grade", "score", "course", "class",
        "program", "faculty", "details of", "information about", "got more than", "above",
        "below", "less than", "greater than", "state", "city", "maharashtra"
    }
    return "student" if any(keyword in query.lower() for keyword in student_keywords) else "general"

def clean_sql(sql: str) -> str:
    sql = re.sub(r'^.*?(SELECT|INSERT|UPDATE|DELETE|SHOW|DESCRIBE)', r'\1', sql, flags=re.IGNORECASE | re.DOTALL)
    sql = re.sub(r';.*$', ';', sql, flags=re.DOTALL)
    sql = ' '.join(sql.split())
    return sql.strip()

def generate_sql(query: str) -> str:
    prompt = f"""
    You are an expert SQL developer. Return ONLY the SQL statement for this query.
    Do NOT add explanations or notes.
    Tables:
    - student_data (roll_no, name, age, gender)
    - student_marks (roll_no, department, subject, marks)
    - student_address (roll_no, address, city, state)
    Query: '{query}'
    """
    response = cached_ollama_response(prompt)
    sql = response.strip()
    sql = clean_sql(sql)
    return sql

def get_general_knowledge(query: str) -> str:
    return cached_ollama_response(query)

def find_aggregate_key(row: dict, keywords: list) -> str:
    for key in row.keys():
        key_norm = re.sub(r'[^a-z0-9]', '', key.lower())
        for word in keywords:
            if word in key_norm:
                return key
    return None

def format_student_results(query: str, results: list) -> str:
    if not results:
        return "No matching records found in the database."

    query_lower = query.lower()
    is_aggregate = any(word in query_lower for word in ["count", "how many", "number of", "average", "avg", "max", "minimum", "min"])

    if is_aggregate:
        row = results[0]
        if any(word in query_lower for word in ["count", "how many", "number of"]):
            count_key = find_aggregate_key(row, ["count"])
            count = row.get(count_key, len(results)) if count_key else len(results)
            return f"There are {count} students matching your query."
        elif any(word in query_lower for word in ["average", "avg"]):
            avg_key = find_aggregate_key(row, ["avg", "average"])
            avg = row.get(avg_key, "N/A")
            return f"The average value is {avg}."
        elif any(word in query_lower for word in ["max"]):
            max_key = find_aggregate_key(row, ["max"])
            max_val = row.get(max_key, "N/A")
            return f"The maximum value is {max_val}."
        elif any(word in query_lower for word in ["minimum", "min"]):
            min_key = find_aggregate_key(row, ["min", "minimum"])
            min_val = row.get(min_key, "N/A")
            return f"The minimum value is {min_val}."

    if len(results) == 1:
        row = results[0]
        details = [f"{col}: {val}" for col, val in row.items()]
        return "Student Details:\n• " + "\n• ".join(details)

    formatted_rows = []
    for row in results:
        row_str = ", ".join([f"{col}: {val}" for col, val in row.items()])
        formatted_rows.append(row_str)
    return f"Found {len(results)} students matching your query:\n" + "\n".join(formatted_rows)

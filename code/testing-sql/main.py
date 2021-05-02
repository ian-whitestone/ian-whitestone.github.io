import os

from jinja2 import Environment, meta, Template
import pandas as pd
from pandas.testing import assert_frame_equal
import pandas.io.sql as psql
import psycopg2

# All these constants would likely live in separate files
CONNECTION = psycopg2.connect(
    host=os.environ['PG_HOST'],
    port=os.environ['PG_PORT'],
    database=os.environ['PG_DBNAME'],
    user=os.environ['PG_USER'],
    password=os.environ['PG_PASSWORD']
)

# Jinja variable name -> production table name mapping
TABLE_XREF = {
    'transactions': 'transactions',
    'users': 'users',
}

BASE_SQL = """
WITH
results AS (
    SELECT
        DATE_PART('doy', t.processed_at) AS day_of_year,
        u.country,
        SUM(amount) AS trxn_volume
    FROM
        {{ transactions }} AS t
        INNER JOIN {{ users }} AS u
            ON t.user_id=u.id
    GROUP BY 1,2
    ORDER BY 1,2
)
SELECT 
    *
FROM 
    results
"""

TEST_DATA = {
    'users': {
        "column_names": ['id', 'country'],
        "values": [
            "(1, 'US')",
            "(2, 'CA')",
            "(3, 'CA')",
        ]
    },
    'transactions': {
        "column_names": ['id', 'user_id', 'amount', 'processed_at'],
        "values": [
            "(1, 1, 15.0, TIMESTAMP'2020-01-01 12:05')",
            "(2, 1, 10.49, TIMESTAMP'2020-01-01 12:10')",
            "(3, 1, -10.49, TIMESTAMP'2020-01-01 12:15')",
            "(4, 2, 25.99, TIMESTAMP'2020-01-02 15:25')",
            "(5, 2, 5.45, TIMESTAMP'2020-01-05 14:01')",
            "(6, 2, 50.5, TIMESTAMP'2020-01-07 03:45')",
            "(7, 3, 49.5, TIMESTAMP'2020-01-07 22:45')",
        ]
    }
}

EXPECTED_RESULTS = {
    'day_of_year': [1, 2, 5, 7],
    'country': ['US', 'CA', 'CA', 'CA'],
    'trxn_volume': [15, 25.99, 5.45, 100]
}

def build_cte(table_ref, table_name):
    values = ",\n".join(TEST_DATA[table_ref]['values'])
    column_names = ",".join(TEST_DATA[table_ref]['column_names'])
    cte = f"""
    {table_name} AS (
        SELECT * FROM (
            VALUES \n{values}
        ) AS t ({column_names})
    ),
    """
    return cte


def inject_cte(sql, cte):
    """
    Add the CTE directly after the WITH statement.
    Could add handling if SQL does not already have a WITH.
    """
    assert sql.strip().startswith('WITH')

    sql_parts = sql.split('WITH')
    return f"WITH{cte}" + sql_parts[1]

def render_sql(mode):
    sql_template = Template(BASE_SQL)
    ast = Environment().parse(BASE_SQL)
    jinja_table_refs = meta.find_undeclared_variables(ast)

    table_prefix = ''
    if mode == 'test':
        # consider generating a random string in case there
        # could actually be a table named test_users or test_transactions
        table_prefix = 'test_'   

    # map Jinja table reference to actual table (or CTE) name
    table_mapping = {
        table_ref: f"{table_prefix}{TABLE_XREF[table_ref]}"
        for table_ref in jinja_table_refs
    }

    sql = sql_template.render(**table_mapping)
    
    if mode == 'test':
        # create & inject the CTEs containing fake data into the SQL
        for table_ref, table_name in table_mapping.items():
            cte = build_cte(table_ref, table_name)
            sql = inject_cte(sql, cte)
    
    return sql


def run_pipeline():
    sql = render_sql(mode='production')
    print(f"Executing SQL:\n{sql}")
    df = psql.read_sql(sql, CONNECTION)

    # run rest of pipeline that relies on data
    # ...

def run_sql_tests():
    sql = render_sql(mode='test')
    print(f"Executing SQL:\n{sql}")
    actual_df = psql.read_sql(sql, CONNECTION)
    expected_df = pd.DataFrame(EXPECTED_RESULTS)

    print(f'Actual dataframe is:\n {actual_df}\nExpected dataframe is:\n{expected_df}')
    # more work required for type checking - need to specify types in the expected results
    assert_frame_equal(actual_df, expected_df, check_dtype=False)
    print('Matchy matchy ✨!')

    # For more advanced comparisons of two dataframes, check out:
    # https://capitalone.github.io/datacompy/
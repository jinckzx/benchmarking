
import sqlite3
import pandas as pd
import os

class SQLMetrics:
    """
    Class for evaluating SQL queries using different metrics
    """
    # Hardcoded database path
    DB_ROOT_PATH = r"D:\data_sci\benchmarking_tool\dataset\spider_data\spider_data\database"
    
    @staticmethod
    def contains_order_by(sql):
        """Check if SQL query contains ORDER BY clause"""
        return "order by" in sql.lower()
    
    @staticmethod
    def exact_match(predicted_sql, ground_truth_sql):
        """
        Compare SQL queries using exact string match
        
        Args:
            predicted_sql (str): The generated SQL query
            ground_truth_sql (str): The ground truth SQL query
            
        Returns:
            bool: True if the queries match exactly (case-insensitive, ignoring whitespace)
        """
        if not predicted_sql or not ground_truth_sql:
            return False
            
        # Normalize both queries by removing extra whitespace and converting to lowercase
        predicted_norm = predicted_sql.lower().strip()
        ground_truth_norm = ground_truth_sql.lower().strip()
        
        return predicted_norm == ground_truth_norm
    
    @staticmethod
    def execution_match(predicted_sql, ground_truth_sql, db_path):
        """
        Compare SQL queries by executing them and comparing results
        
        Args:
            predicted_sql (str): The generated SQL query
            ground_truth_sql (str): The ground truth SQL query
            db_path (str): Path to the SQLite database file
            
        Returns:
            bool: True if both queries produce the same results, False otherwise
        """
        if not predicted_sql or not ground_truth_sql:
            return False
            
        try:
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                
                # Execute the predicted query
                cursor.execute(predicted_sql)
                predicted_res = cursor.fetchall()
                
                # Execute the ground truth query
                cursor.execute(ground_truth_sql)
                ground_truth_res = cursor.fetchall()
                
                # Compare results based on whether there's ORDER BY
                if SQLMetrics.contains_order_by(predicted_sql) or SQLMetrics.contains_order_by(ground_truth_sql):
                    # If ORDER BY exists, order matters
                    result = (predicted_res == ground_truth_res)
                else:
                    # If no ORDER BY, order doesn't matter
                    result = (sorted(map(tuple, predicted_res)) == sorted(map(tuple, ground_truth_res)))
                
                return result
                
        except Exception as e:
            # Return False for any execution errors
            print(f"Execution error: {str(e)}")
            return False
    
    @staticmethod
    def get_db_path(db_id):
        """
        Get the full path to a database file
        
        Args:
            db_id (str): The database ID
            
        Returns:
            str: Full path to the SQLite database file
        """
        return os.path.join(SQLMetrics.DB_ROOT_PATH, db_id, f"{db_id}.sqlite")
    
    @staticmethod
    def evaluate_query(predicted_sql, ground_truth_sql, db_id):
        """
        Evaluate a query using both exact match and execution match
        
        Args:
            predicted_sql (str): The generated SQL query
            ground_truth_sql (str): The ground truth SQL query
            db_id (str): The database ID
            
        Returns:
            dict: Results containing exact_match and execution_match booleans
        """
        exact = SQLMetrics.exact_match(predicted_sql, ground_truth_sql)
        
        execution = False
        db_path = SQLMetrics.get_db_path(db_id)
        if os.path.exists(db_path):
            execution = SQLMetrics.execution_match(predicted_sql, ground_truth_sql, db_path)
            
        return {
            "exact_match": exact,
            "execution_match": execution
        }
    
    @staticmethod
    def compute_metrics(results_df):
        """
        Compute overall metrics from a dataframe of results
        
        Args:
            results_df (pd.DataFrame): DataFrame with exact_match and execution_match columns
            
        Returns:
            dict: Overall metrics including accuracy percentages
        """
        total = len(results_df)
        
        if total == 0:
            return {
                "exact_match_count": 0,
                "execution_match_count": 0,
                "exact_match_rate": 0.0,
                "execution_match_rate": 0.0,
                "total": 0
            }
        
        # Convert to numeric values (True becomes 1, False becomes 0)
        exact_matches = results_df["exact_match"].astype(int).sum()
        exec_matches = results_df["execution_match"].astype(int).sum()
        
        return {
            "exact_match_count": exact_matches,
            "execution_match_count": exec_matches,
            "exact_match_rate": (exact_matches / total) * 100,
            "execution_match_rate": (exec_matches / total) * 100,
            "total": total
        }
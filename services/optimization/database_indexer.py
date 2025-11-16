"""
Database indexing optimization service
Manages database indexes for improved query performance
"""

import logging
from typing import Dict, Any, List, Optional
from sqlalchemy import text, inspect
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session
from database.db import engine as default_engine

logger = logging.getLogger(__name__)


class DatabaseIndexer:
    """
    Database index management and optimization
    """
    
    def __init__(self, engine: Engine = None):
        """
        Initialize database indexer
        
        Args:
            engine: SQLAlchemy engine (uses global engine if not provided)
        """
        self.engine = engine or default_engine
        self._inspector = None
    
    def _get_inspector(self):
        """Get SQLAlchemy inspector"""
        if self._inspector is None:
            self._inspector = inspect(self.engine)
        return self._inspector
    
    def get_existing_indexes(self, table_name: str) -> List[Dict[str, Any]]:
        """
        Get existing indexes for a table
        
        Args:
            table_name: Name of the table
            
        Returns:
            List of index information dictionaries
        """
        try:
            inspector = self._get_inspector()
            indexes = inspector.get_indexes(table_name)
            return indexes
        except Exception as e:
            logger.error(f"Error getting indexes for {table_name}: {e}")
            return []
    
    def create_index(self, table_name: str, columns: List[str], 
                    index_name: Optional[str] = None, unique: bool = False) -> bool:
        """
        Create an index on a table
        
        Args:
            table_name: Name of the table
            columns: List of column names to index
            index_name: Optional index name (auto-generated if not provided)
            unique: Whether the index should be unique
            
        Returns:
            True if index was created successfully
        """
        if not index_name:
            index_name = f"idx_{table_name}_{'_'.join(columns)}"
        
        columns_str = ', '.join(columns)
        unique_str = "UNIQUE" if unique else ""
        
        # Check if index already exists
        existing_indexes = self.get_existing_indexes(table_name)
        if any(idx['name'] == index_name for idx in existing_indexes):
            logger.info(f"Index {index_name} already exists on {table_name}")
            return True
        
        try:
            # SQLite uses CREATE INDEX IF NOT EXISTS
            # PostgreSQL uses CREATE INDEX IF NOT EXISTS
            sql = f"CREATE {unique_str} INDEX IF NOT EXISTS {index_name} ON {table_name}({columns_str})"
            
            with self.engine.connect() as conn:
                conn.execute(text(sql))
                conn.commit()
            
            logger.info(f"Created index {index_name} on {table_name}({columns_str})")
            return True
        except Exception as e:
            logger.error(f"Error creating index {index_name}: {e}")
            return False
    
    def drop_index(self, table_name: str, index_name: str) -> bool:
        """
        Drop an index
        
        Args:
            table_name: Name of the table
            index_name: Name of the index to drop
            
        Returns:
            True if index was dropped successfully
        """
        try:
            # Check if index exists
            existing_indexes = self.get_existing_indexes(table_name)
            if not any(idx['name'] == index_name for idx in existing_indexes):
                logger.info(f"Index {index_name} does not exist on {table_name}")
                return True
            
            # SQLite uses DROP INDEX IF EXISTS
            # PostgreSQL uses DROP INDEX IF EXISTS
            sql = f"DROP INDEX IF EXISTS {index_name}"
            
            with self.engine.connect() as conn:
                conn.execute(text(sql))
                conn.commit()
            
            logger.info(f"Dropped index {index_name} from {table_name}")
            return True
        except Exception as e:
            logger.error(f"Error dropping index {index_name}: {e}")
            return False
    
    def analyze_indexes(self, table_name: str) -> Dict[str, Any]:
        """
        Analyze indexes for a table
        
        Args:
            table_name: Name of the table
            
        Returns:
            Dictionary with index analysis
        """
        try:
            inspector = self._get_inspector()
            indexes = inspector.get_indexes(table_name)
            columns = [col['name'] for col in inspector.get_columns(table_name)]
            
            # Analyze index coverage
            indexed_columns = set()
            for idx in indexes:
                indexed_columns.update(idx.get('column_names', []))
            
            unindexed_columns = set(columns) - indexed_columns
            
            return {
                'table_name': table_name,
                'total_indexes': len(indexes),
                'indexes': indexes,
                'indexed_columns': list(indexed_columns),
                'unindexed_columns': list(unindexed_columns),
                'coverage': len(indexed_columns) / len(columns) * 100 if columns else 0
            }
        except Exception as e:
            logger.error(f"Error analyzing indexes for {table_name}: {e}")
            return {
                'table_name': table_name,
                'error': str(e)
            }
    
    def recommend_indexes(self, table_name: str, query_patterns: List[str]) -> List[Dict[str, Any]]:
        """
        Recommend indexes based on query patterns
        
        Args:
            table_name: Name of the table
            query_patterns: List of SQL query patterns (normalized)
            
        Returns:
            List of index recommendations
        """
        recommendations = []
        
        # Analyze query patterns to find frequently queried columns
        column_usage = {}
        for query in query_patterns:
            query_lower = query.lower()
            # Simple pattern matching for WHERE clauses
            if 'where' in query_lower:
                # Extract column names (simplified)
                # In production, use SQL parser
                for col in self._extract_columns_from_query(query):
                    column_usage[col] = column_usage.get(col, 0) + 1
        
        # Recommend indexes for frequently used columns
        sorted_columns = sorted(column_usage.items(), key=lambda x: x[1], reverse=True)
        
        for col, usage_count in sorted_columns[:5]:  # Top 5
            if usage_count > 5:  # Only if used frequently
                recommendations.append({
                    'table': table_name,
                    'columns': [col],
                    'index_name': f"idx_{table_name}_{col}",
                    'reason': f'Column used in {usage_count} queries',
                    'priority': 'high' if usage_count > 20 else 'medium'
                })
        
        return recommendations
    
    def _extract_columns_from_query(self, query: str) -> List[str]:
        """
        Extract column names from query (simplified)
        In production, use a proper SQL parser
        
        Args:
            query: SQL query string
            
        Returns:
            List of column names
        """
        # Very simplified extraction
        # In production, use sqlparse or similar
        columns = []
        query_lower = query.lower()
        
        # Look for common patterns
        if 'where' in query_lower:
            # Extract after WHERE
            where_part = query_lower.split('where')[1].split()[0]
            if where_part and where_part not in ['and', 'or', 'not']:
                columns.append(where_part)
        
        return columns
    
    def optimize_table_indexes(self, table_name: str) -> Dict[str, Any]:
        """
        Optimize indexes for a table
        
        Args:
            table_name: Name of the table
            
        Returns:
            Dictionary with optimization results
        """
        analysis = self.analyze_indexes(table_name)
        
        # Check for duplicate indexes
        indexes = analysis.get('indexes', [])
        duplicate_indexes = []
        seen_columns = {}
        
        for idx in indexes:
            col_key = tuple(sorted(idx.get('column_names', [])))
            if col_key in seen_columns:
                duplicate_indexes.append({
                    'index1': seen_columns[col_key],
                    'index2': idx['name'],
                    'columns': list(col_key)
                })
            else:
                seen_columns[col_key] = idx['name']
        
        return {
            'table_name': table_name,
            'analysis': analysis,
            'duplicate_indexes': duplicate_indexes,
            'recommendations': {
                'remove_duplicates': len(duplicate_indexes) > 0,
                'add_indexes': len(analysis.get('unindexed_columns', [])) > 0
            }
        }
    
    def create_recommended_indexes(self, recommendations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create indexes from recommendations
        
        Args:
            recommendations: List of index recommendations
            
        Returns:
            Dictionary with creation results
        """
        results = {
            'created': 0,
            'failed': 0,
            'skipped': 0,
            'details': []
        }
        
        for rec in recommendations:
            table_name = rec.get('table')
            columns = rec.get('columns', [])
            index_name = rec.get('index_name')
            unique = rec.get('unique', False)
            
            if not table_name or not columns:
                results['skipped'] += 1
                results['details'].append({
                    'recommendation': rec,
                    'status': 'skipped',
                    'reason': 'Missing table or columns'
                })
                continue
            
            success = self.create_index(table_name, columns, index_name, unique)
            if success:
                results['created'] += 1
                results['details'].append({
                    'recommendation': rec,
                    'status': 'created'
                })
            else:
                results['failed'] += 1
                results['details'].append({
                    'recommendation': rec,
                    'status': 'failed'
                })
        
        return results


# Global database indexer instance
_database_indexer: Optional[DatabaseIndexer] = None


def get_database_indexer() -> DatabaseIndexer:
    """Get or create global database indexer instance"""
    global _database_indexer
    if _database_indexer is None:
        _database_indexer = DatabaseIndexer(default_engine)
    return _database_indexer


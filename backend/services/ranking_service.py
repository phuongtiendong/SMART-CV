"""Ranking service for CVs."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

import logging
from typing import List, Optional

import pandas as pd
import sqlite3

from config import DB_PATH

logger = logging.getLogger(__name__)


class RankingService:
    """Service for retrieving and managing CV rankings."""
    
    @staticmethod
    def get_ranking(job_id: Optional[int] = None) -> pd.DataFrame:
        """
        Get ranking of candidates.
        
        Args:
            job_id: Optional job ID to filter by. If None, returns all candidates.
            
        Returns:
            DataFrame with candidate rankings
        """
        with sqlite3.connect(DB_PATH) as conn:
            if job_id:
                df = pd.read_sql_query(
                    """
                    SELECT a.id, a.job_id, j.title as job_title, a.name, a.email, a.phone, 
                           a.score, a.created_at
                    FROM analyses a
                    JOIN jobs j ON a.job_id = j.id
                    WHERE a.job_id = ?
                    ORDER BY a.score DESC, a.id DESC
                    """,
                    conn,
                    params=(job_id,)
                )
            else:
                df = pd.read_sql_query(
                    """
                    SELECT a.id, a.job_id, j.title as job_title, a.name, a.email, a.phone, 
                           a.score, a.created_at
                    FROM analyses a
                    JOIN jobs j ON a.job_id = j.id
                    ORDER BY a.score DESC, a.id DESC
                    """,
                    conn
                )
        return df
    
    @staticmethod
    def get_ranking_dict(job_id: Optional[int] = None) -> List[dict]:
        """
        Get ranking as a list of dictionaries.
        
        Args:
            job_id: Optional job ID to filter by.
            
        Returns:
            List of dictionaries with candidate information
        """
        df = RankingService.get_ranking(job_id)
        return df.to_dict('records')

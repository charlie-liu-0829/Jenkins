from __future__ import annotations

import logging
import re

import pymysql
from pymysql.cursors import DictCursor

logger = logging.getLogger(__name__)


class SqlUtil:
    def __init__(
        self,
        database: str = "ecommerce_demo",
        charset: str = "utf8mb4",
        host: str = "localhost",
        port: int = 3306,
        user: str = "root",
        password: str = "",
    ):
        self.host, self.port, self.user = host, port, user
        self.password, self.database, self.charset = password, database, charset
        self.conn = None
        self.cursor = None

    def connect(self):
        try:
            self.conn = pymysql.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
                charset=self.charset,
                cursorclass=DictCursor,
            )
            self.cursor = self.conn.cursor()
            logger.info("数据库连接成功: %s:%s/%s", self.host, self.port, self.database)
        except Exception:
            logger.exception("数据库连接失败")
            raise

    def execute_sql(self, sql: str, args=None):
        if not isinstance(sql, str) or not sql.strip():
            raise ValueError("sql must be a non-empty string")
        if not self.conn or not self.conn.open:
            self.connect()
        try:
            params = () if args is None else args
            logger.info("执行 SQL: %s", _redact_sql(sql))
            self.cursor.execute(sql, params)
            # ``cursor.description`` also handles CTEs and other statements
            # that return rows even when they do not start with SELECT.
            if self.cursor.description is not None:
                return self.cursor.fetchall()
            self.conn.commit()
            return self.cursor.rowcount
        except Exception:
            self.conn.rollback()
            logger.exception("SQL 执行异常，已回滚: %s", _redact_sql(sql))
            raise

    def execute_many(self, sql: str, args):
        if not args:
            return 0
        if not self.conn or not self.conn.open:
            self.connect()
        try:
            affected = self.cursor.executemany(sql, args)
            self.conn.commit()
            return affected
        except Exception:
            self.conn.rollback()
            logger.exception("批量 SQL 执行异常，已回滚")
            raise

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
        self.cursor = self.conn = None
        logger.info("数据库连接已关闭")

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, *_exc):
        self.close()


_SQL_COMMENT = re.compile(r"^(?:/\*.*?\*/|--[^\n]*|#[^\n]*)\s*", re.S)


def _statement_type(sql: str) -> str:
    stripped = _SQL_COMMENT.sub("", sql.strip()).lower()
    return stripped.split(None, 1)[0] if stripped else ""


def _redact_sql(sql: str) -> str:
    return re.sub(r"(?i)(password\s*=\s*)(('[^']*')|(\"[^\"]*\"))", r"\1'***'", sql)

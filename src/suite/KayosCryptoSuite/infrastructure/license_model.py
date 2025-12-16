# infrastructure/license_model.py

from sqlalchemy import (Table, Column, Integer, String, Date, MetaData,
                        DateTime, func)

metadata = MetaData()

license_logs = Table(
    'license_logs',
    metadata,
    Column('id', Integer, primary_key=True),
    # --- INÍCIO DA MUDANÇA ---
    Column('license_id', String(36), nullable=False, unique=True, index=True),
    Column('operation', String(50), nullable=False),
    Column('status', String(20), nullable=False, default='active'),
    # --- FIM DA MUDANÇA ---
    Column('user_name', String(100)),
    Column('email', String(100)),
    Column('level', String(50)),
    Column('expiration', Date),
    Column('timestamp', DateTime, default=func.now(), onupdate=func.now())
)

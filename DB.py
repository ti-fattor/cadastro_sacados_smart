from sqlalchemy import (
    create_engine, Column, Integer, String, Enum, ForeignKey, Table, UniqueConstraint, Boolean
)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from enum import Enum as PyEnum
import pandas as pd


DB_HOST = '192.168.0.231'
DB_USER = 'google'
DB_PASSWORD = 'IK627MulPuL2MS5TC7t2'
DB_NAME = 'cedentes_sacados'


DATABASE_URL =f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:3306/cedentes_sacados"
engine =create_engine(DATABASE_URL, echo=True)
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()


# Enum para tipo de documento e tipo de referência


class TipoDocumento(PyEnum):
    PF = 'PF'
    PJ = 'PJ'

class TipoReferencia(PyEnum):
    sacado = 'sacado'
    cedente = 'cedente'

# Tabela associativa: muitos para muitos (cedente <-> sacado)
cedente_sacado = Table(
    'cedente_sacado',
    Base.metadata,
    Column('sacado_id', Integer, ForeignKey('empresas.id', ondelete='CASCADE'), primary_key=True),
    Column('cedente_id', Integer, ForeignKey('empresas.id', ondelete='CASCADE'), primary_key=True)
)

# Tabela Controlador
class Controlador(Base):
    __tablename__ = 'controlador'

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(40), nullable=False)
    id_dac = Column(String(5))

    empresas = relationship("Empresa", back_populates="controlador_ref")

# Tabela Empresa (cedente ou sacado)
class Empresa(Base):
    __tablename__ = 'empresas'

    id = Column(Integer, primary_key=True, autoincrement=True)
    nome = Column(String(255), nullable=False)
    tipo_documento = Column(Enum(TipoDocumento), nullable=False)
    cnpj_cpf = Column(String(14), unique=True, nullable=False)
    tempo_tranche = Column(String(4))
    controlador = Column(Integer, ForeignKey('controlador.id', ondelete='CASCADE'))
    ph3a = Column(Boolean, default=False)

    controlador_ref = relationship("Controlador", back_populates="empresas")
    emails = relationship("Email", back_populates="empresa", cascade="all, delete")
    telefones = relationship("Telefone", back_populates="empresa", cascade="all, delete-orphan")
    sacados = relationship(
        'Empresa',
        secondary=cedente_sacado,
        primaryjoin=id == cedente_sacado.c.cedente_id,
        secondaryjoin=id == cedente_sacado.c.sacado_id,
        backref='cedentes'
    )

# Tabela Emails
class Email(Base):
    __tablename__ = 'emails'

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), nullable=False)
    empresa_id = Column(Integer, ForeignKey('empresas.id', ondelete='CASCADE'), nullable=False)

    empresa = relationship("Empresa", back_populates="emails")

    __table_args__ = (
        UniqueConstraint('email', 'empresa_id'),
    )

# Tabela Telefones
class Telefone(Base):
    __tablename__ = 'telefones'

    id = Column(Integer, primary_key=True, autoincrement=True)
    ddd = Column(String(3))
    telefone = Column(String(20), nullable=False)
    empresa_id = Column(Integer, ForeignKey('empresas.id', ondelete='CASCADE'), nullable=False)
    empresa = relationship("Empresa", back_populates="telefones")

    __table_args__ = (
        UniqueConstraint('ddd','telefone', 'empresa_id'),
    )

if __name__ == "__main__":
    df = pd.read_sql("SELECT * FROM telefones", con=DATABASE_URL)
    # Exportar para Excel
    df.to_excel("telefones.xlsx", index=False)

    print("Exportação concluída: telefones.xlsx")
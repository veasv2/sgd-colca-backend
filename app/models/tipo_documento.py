# app/models/tipo_documento.py
"""
Modelo de TipoDocumento para SGD-Colca (Simplificado)
Catálogo básico de tipos de documentos municipales
"""
from sqlalchemy import Column, String, Text, Integer, Boolean
from sqlalchemy.orm import relationship
from .base import BaseModel


class TipoDocumento(BaseModel):
    __tablename__ = "tipo_documento"
    
    # === IDENTIFICACIÓN BÁSICA ===
    codigo = Column(String(20), unique=True, nullable=False, index=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text, nullable=True)
    
    # === CATEGORIZACIÓN ===
    categoria = Column(String(50), nullable=True)  # INTERNO, EXTERNO, RESOLUCION, NORMATIVO
    subcategoria = Column(String(50), nullable=True)  # COMUNICACION, INFORME, SOLICITUD, ADMINISTRATIVO
    
    # === CONFIGURACIÓN BÁSICA DE NUMERACIÓN ===
    prefijo_correlativo = Column(String(10), nullable=False)  # OF, INF, MEMO, RA, etc.
    
    # === PRESENTACIÓN Y ORGANIZACIÓN ===
    orden_presentacion = Column(Integer, default=0)  # Para ordenar en listas
    es_frecuente = Column(Boolean, default=False)  # Para mostrar primero en interfaces
    
    # === ESTADO ===
    # activo ya está en BaseModel
    
    # === RELACIONES ===
    
    # Relación 1:1 con configuración
    configuracion = relationship(
        "TipoDocumentoConfiguracion", 
        back_populates="tipo_documento", 
        uselist=False,  # Asegura relación 1:1
        cascade="all, delete-orphan"
    )
    
    # Relación 1:N con documentos
    documentos = relationship("Documento", back_populates="tipo_documento")
    
    def __repr__(self):
        return f"<TipoDocumento(codigo='{self.codigo}', nombre='{self.nombre}')>"
    
    def generar_numero_correlativo(self, año: int, correlativo: int, unidad_codigo: str = None) -> str:
        """
        Genera el número correlativo según la configuración
        """
        formato = self.configuracion.formato_numeracion if self.configuracion else "{prefijo}-{año}-{correlativo:04d}"
        
        return formato.format(
            prefijo=self.prefijo_correlativo,
            año=año,
            correlativo=correlativo,
            unidad=unidad_codigo or ""
        )
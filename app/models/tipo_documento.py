# En app/models/tipo_documento.py

from sqlalchemy import Column, String, Text, Integer, Boolean
from sqlalchemy.orm import relationship
from .base import BaseModel # Asumiendo que BaseModel define id, created_at, updated_at, y activo

class TipoDocumento(BaseModel):
    __tablename__ = "tipo_documento" # La tabla principal para los tipos de documento
    
    # === IDENTIFICACIÓN BÁSICA ===
    codigo = Column(String(20), unique=True, nullable=False, index=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text, nullable=True)
    
    # === CATEGORIZACIÓN ===
    categoria = Column(String(50), nullable=True)   # INTERNO, EXTERNO, RESOLUCION, NORMATIVO
    subcategoria = Column(String(50), nullable=True) # COMUNICACION, INFORME, SOLICITUD, ADMINISTRATIVO
    
    # === CONFIGURACIÓN BÁSICA DE NUMERACIÓN ===
    prefijo_correlativo = Column(String(10), nullable=False) # OF, INF, MEMO, RA, etc.
    formato_numeracion = Column(String(100), default="{prefijo}-{año}-{correlativo:04d}")
    correlativo_por_unidad = Column(Boolean, default=False)
    
    # === VISIBILIDAD ===
    es_publico = Column(Boolean, default=False)
    
    # === ADJUNTOS ===
    permite_adjuntos = Column(Boolean, default=True)
    max_adjuntos = Column(Integer, default=5)
    
    # === REQUISITOS DEL DOCUMENTO ===
    requiere_destinatario_interno = Column(Boolean, default=True)
    requiere_destinatario_externo = Column(Boolean, default=False)
    requiere_visto_bueno = Column(Boolean, default=False)
    
    # === GOOGLE DRIVE (Plantillas) ===
    plantilla_gdoc_id = Column(String(200), nullable=True) # ID de la plantilla de Google Docs
    
    # === PRESENTACIÓN Y ORGANIZACIÓN ===
    orden_presentacion = Column(Integer, default=0)   # Para ordenar en listas
    es_frecuente = Column(Boolean, default=False)     # Para mostrar primero en interfaces
    
    # === RELACIONES ===
    # Relación 1:N con documentos (los documentos de este tipo)
    documentos = relationship("Documento", back_populates="tipo_documento")
    
    def __repr__(self):
        return f"<TipoDocumento(codigo='{self.codigo}', nombre='{self.nombre}')>"
    
    def generar_numero_correlativo(self, año: int, correlativo: int, unidad_codigo: str = None) -> str:
        """
        Genera el número correlativo según la configuración de este tipo de documento.
        """
        # El formato ahora se lee directamente del campo del modelo
        formato = self.formato_numeracion if self.formato_numeracion else "{prefijo}-{año}-{correlativo:04d}"
        
        # Si el correlativo es por unidad y se proporciona el código de unidad
        if self.correlativo_por_unidad and unidad_codigo:
            # Asegura que el formato pueda manejar el campo 'unidad'
            if "{unidad}" not in formato:
                # Si el formato no incluye {unidad}, puedes decidir si lo añades por defecto
                # o si lanzas un error. Aquí, lo añadimos si la config lo requiere.
                formato += "-{unidad}" 
            
        return formato.format(
            prefijo=self.prefijo_correlativo,
            año=año,
            correlativo=correlativo,
            unidad=unidad_codigo or "" # Proporciona una cadena vacía si no hay unidad_codigo
        )
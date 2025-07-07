# app/utils/filter_engine.py

from typing import Any, List, Type
from sqlalchemy.orm import Query, Session
from sqlalchemy import or_, and_, Column
import math

from app.schemas.common.filter_schemas import (
    StringFilter,
    NumberFilter,
    DateFilter,
    EnumFilter,
    BooleanFilter,
    PaginationConfig
)

class FilterEngine:
    
    @staticmethod
    def apply_filters(query: Query, model_class: Type[Any], where_filters: Any) -> Query:
        if not where_filters:
            return query
            
        conditions = FilterEngine._build_conditions(model_class, where_filters)
        
        if conditions:
            # Si hay múltiples condiciones al nivel raíz, aplicar AND implícito
            if len(conditions) == 1:
                query = query.filter(conditions[0])
            else:
                query = query.filter(and_(*conditions))
            
        return query
    
    @staticmethod
    def apply_pagination(query: Query, pagination: PaginationConfig) -> tuple[List[Any], dict]:
        # Contar total antes de paginación
        total = query.count()
        
        # Calcular offset
        page = pagination.page
        page_size = pagination.pageSize
        offset = (page - 1) * page_size
        
        # Aplicar paginación
        data = query.offset(offset).limit(page_size).all()
        
        # Calcular metadata
        total_pages = math.ceil(total / page_size) if total > 0 else 1
        inicio = offset + 1 if total > 0 else 0
        fin = min(offset + page_size, total)
        
        metadata = {
            "total": total,
            "inicio": inicio,
            "fin": fin,
            "totalPages": total_pages,
            "hasNextPage": page < total_pages,
            "hasPrevPage": page > 1,
            "currentPage": page
        }
        
        return data, metadata
    
    @staticmethod
    def _build_conditions(model_class: Type[Any], where_filters: Any) -> List[Any]:
        conditions = []
        
        print(f"🔧 FILTER ENGINE DEBUG:")
        print(f"   - where_filters: {where_filters}")
        print(f"   - where_filters type: {type(where_filters)}")
        print(f"   - where_filters vars: {vars(where_filters) if hasattr(where_filters, '__dict__') else 'No vars'}")
        
        # Verificar AND/OR
        has_and = hasattr(where_filters, 'AND') and where_filters.AND
        has_or = hasattr(where_filters, 'OR') and where_filters.OR
        print(f"   - Tiene AND: {has_and}")
        print(f"   - Tiene OR: {has_or}")
        
        # Manejar AND anidado
        if has_and:
            print(f"   - Procesando AND...")
            and_conditions = []
            for and_condition in where_filters.AND:
                sub_conditions = FilterEngine._build_conditions(model_class, and_condition)
                if sub_conditions:
                    # Si hay múltiples sub-condiciones, unirlas con AND
                    if len(sub_conditions) == 1:
                        and_conditions.append(sub_conditions[0])
                    else:
                        and_conditions.append(and_(*sub_conditions))
            
            if and_conditions:
                # Todas las condiciones AND deben cumplirse
                if len(and_conditions) == 1:
                    conditions.append(and_conditions[0])
                else:
                    conditions.append(and_(*and_conditions))
        
        # Manejar OR anidado
        elif has_or:
            print(f"   - Procesando OR...")
            or_conditions = []
            for or_condition in where_filters.OR:
                sub_conditions = FilterEngine._build_conditions(model_class, or_condition)
                if sub_conditions:
                    # Si hay múltiples sub-condiciones en un OR, unirlas con AND
                    if len(sub_conditions) == 1:
                        or_conditions.append(sub_conditions[0])
                    else:
                        or_conditions.append(and_(*sub_conditions))
            
            if or_conditions:
                # Al menos una de las condiciones OR debe cumplirse
                conditions.append(or_(*or_conditions))
        
        # ✅ PROCESAR FILTROS INDIVIDUALES (cuando NO hay AND/OR)
        else:
            print(f"   - Procesando filtros individuales...")
            
            for field_name, filter_value in vars(where_filters).items():
                print(f"   - Campo: {field_name}, Valor: {filter_value}, Tipo: {type(filter_value)}")
                
                if field_name in ['AND', 'OR'] or filter_value is None:
                    print(f"     -> Saltando campo {field_name}")
                    continue
                    
                # Obtener el campo del modelo
                if hasattr(model_class, field_name):
                    model_field = getattr(model_class, field_name)
                    print(f"     -> Campo del modelo encontrado: {model_field}")
                    
                    field_conditions = FilterEngine._apply_field_filter(model_field, filter_value)
                    print(f"     -> Condiciones generadas: {field_conditions}")
                    
                    conditions.extend(field_conditions)
                else:
                    print(f"     -> Campo {field_name} NO encontrado en modelo {model_class}")
        
        print(f"   - Condiciones finales: {conditions}")
        return conditions
    
    @staticmethod
    def _apply_field_filter(model_field: Column, filter_obj: Any) -> List[Any]:
        conditions = []
        
        print(f"🔧 APPLY FIELD FILTER:")
        print(f"   - model_field: {model_field}")
        print(f"   - filter_obj: {filter_obj}")
        print(f"   - filter_obj type: {type(filter_obj)}")
        
        # Determinar tipo de filtro y aplicar
        if isinstance(filter_obj, StringFilter):
            print(f"   - Es StringFilter")
            conditions.extend(FilterEngine._apply_string_filter(model_field, filter_obj))
        elif isinstance(filter_obj, NumberFilter):
            print(f"   - Es NumberFilter")
            conditions.extend(FilterEngine._apply_number_filter(model_field, filter_obj))
        elif isinstance(filter_obj, DateFilter):
            print(f"   - Es DateFilter")
            conditions.extend(FilterEngine._apply_date_filter(model_field, filter_obj))
        elif isinstance(filter_obj, EnumFilter):
            print(f"   - Es EnumFilter")
            conditions.extend(FilterEngine._apply_enum_filter(model_field, filter_obj))
        elif isinstance(filter_obj, BooleanFilter):
            print(f"   - Es BooleanFilter")
            conditions.extend(FilterEngine._apply_boolean_filter(model_field, filter_obj))
        else:
            print(f"   - Tipo de filtro NO RECONOCIDO: {type(filter_obj)}")
        
        print(f"   - Condiciones del campo: {conditions}")
        return conditions
    
    @staticmethod
    def _apply_string_filter(field: Column, string_filter: StringFilter) -> List[Any]:
        conditions = []
        
        if string_filter.equals is not None:
            conditions.append(field == string_filter.equals)
        
        if string_filter.contains is not None:
            conditions.append(field.ilike(f"%{string_filter.contains}%"))
        
        if string_filter.startsWith is not None:
            conditions.append(field.ilike(f"{string_filter.startsWith}%"))
        
        if string_filter.endsWith is not None:
            conditions.append(field.ilike(f"%{string_filter.endsWith}"))
        
        # Verificar ambos atributos posibles para 'in'
        in_value = None
        if hasattr(string_filter, 'in_') and string_filter.in_ is not None:
            in_value = string_filter.in_
        elif hasattr(string_filter, 'in') and getattr(string_filter, 'in') is not None:
            in_value = getattr(string_filter, 'in')
        
        if in_value is not None and len(in_value) > 0:
            conditions.append(field.in_(in_value))
        
        return conditions
    
    @staticmethod
    def _apply_number_filter(field: Column, number_filter: NumberFilter) -> List[Any]:
        """Aplica filtros numéricos"""
        conditions = []
        
        if number_filter.equals is not None:
            conditions.append(field == number_filter.equals)
        
        if number_filter.gt is not None:
            conditions.append(field > number_filter.gt)
        
        if number_filter.gte is not None:
            conditions.append(field >= number_filter.gte)
        
        if number_filter.lt is not None:
            conditions.append(field < number_filter.lt)
        
        if number_filter.lte is not None:
            conditions.append(field <= number_filter.lte)
        
        # Verificar ambos atributos posibles para 'in'
        in_value = None
        if hasattr(number_filter, 'in_') and number_filter.in_ is not None:
            in_value = number_filter.in_
        elif hasattr(number_filter, 'in') and getattr(number_filter, 'in') is not None:
            in_value = getattr(number_filter, 'in')
        
        if in_value is not None and len(in_value) > 0:
            conditions.append(field.in_(in_value))
        
        return conditions
    
    @staticmethod
    def _apply_date_filter(field: Column, date_filter: DateFilter) -> List[Any]:
        """Aplica filtros de fecha"""
        conditions = []
        
        if date_filter.equals is not None:
            conditions.append(field == date_filter.equals)
        
        if date_filter.gt is not None:
            conditions.append(field > date_filter.gt)
        
        if date_filter.gte is not None:
            conditions.append(field >= date_filter.gte)
        
        if date_filter.lt is not None:
            conditions.append(field < date_filter.lt)
        
        if date_filter.lte is not None:
            conditions.append(field <= date_filter.lte)
        
        # Verificar ambos atributos posibles para 'in'
        in_value = None
        if hasattr(date_filter, 'in_') and date_filter.in_ is not None:
            in_value = date_filter.in_
        elif hasattr(date_filter, 'in') and getattr(date_filter, 'in') is not None:
            in_value = getattr(date_filter, 'in')
        
        if in_value is not None and len(in_value) > 0:
            conditions.append(field.in_(in_value))
        
        return conditions
    
    @staticmethod
    def _apply_enum_filter(field: Column, enum_filter: EnumFilter) -> List[Any]:
        """Aplica filtros de enum"""
        conditions = []
        
        print(f"🔧 ENUM FILTER DEBUG:")
        print(f"   - field: {field}")
        print(f"   - enum_filter: {enum_filter}")
        print(f"   - enum_filter type: {type(enum_filter)}")
        print(f"   - enum_filter vars: {vars(enum_filter)}")
        
        if enum_filter.equals is not None:
            print(f"   - Aplicando equals: {enum_filter.equals}")
            conditions.append(field == enum_filter.equals)
        
        # Verificar ambos atributos posibles para 'in'
        in_value = None
        if hasattr(enum_filter, 'in_') and enum_filter.in_ is not None:
            in_value = enum_filter.in_
            print(f"   - Encontrado in_ con valor: {in_value}")
        elif hasattr(enum_filter, 'in') and getattr(enum_filter, 'in') is not None:
            in_value = getattr(enum_filter, 'in')
            print(f"   - Encontrado in con valor: {in_value}")
        else:
            print(f"   - NO se encontró valor 'in' válido")
            print(f"   - Tiene in_?: {hasattr(enum_filter, 'in_')}")
            print(f"   - Valor in_: {getattr(enum_filter, 'in_', 'NO EXISTE')}")
            print(f"   - Tiene in?: {hasattr(enum_filter, 'in')}")
            print(f"   - Valor in: {getattr(enum_filter, 'in', 'NO EXISTE')}")
        
        if in_value is not None and len(in_value) > 0:
            print(f"   - Aplicando IN con valores: {in_value}")
            conditions.append(field.in_(in_value))
        else:
            print(f"   - NO se aplicará filtro IN (in_value: {in_value})")
        
        print(f"   - Condiciones generadas: {conditions}")
        return conditions
    
    @staticmethod
    def _apply_boolean_filter(field: Column, boolean_filter: BooleanFilter) -> List[Any]:
        """Aplica filtros booleanos"""
        conditions = []
        
        if boolean_filter.equals is not None:
            conditions.append(field == boolean_filter.equals)
        
        return conditions
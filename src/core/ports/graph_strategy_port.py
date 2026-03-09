from abc import ABC, abstractmethod
from typing import Dict, Callable, Any
from langgraph.graph import StateGraph

class GraphStrategyPort(ABC):
    """Puerto para diferentes estrategias de construcción de grafos"""
    
    @abstractmethod
    def build_graph(
        self,
        state_schema: Any,
        node_functions: Dict[str, Callable],
        **kwargs
    ) -> StateGraph:
        """Construye un grafo según la estrategia específica"""
        pass
    
    @abstractmethod
    def get_required_node_functions(self) -> list[str]:
        """Retorna los nombres de las funciones de nodo requeridas"""
        pass
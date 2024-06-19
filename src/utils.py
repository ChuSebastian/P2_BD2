# funciones auxiliares: calculo TF-IDF, normalizacion de vectores, etc
from typing import TypeVar,Generic, List, Optional
# https://www.javatpoint.com/min-heap-implementation-in-python
T = TypeVar('T')

class MinHeap(Generic[T]):
    def __init__(self, val: Optional[List[T]] = None):  
        self.heap: List[T] = []
        if val is not None:
            self.build_heap(val)
        
    def parent(self, i: int) -> int:  
        return (i - 1) // 2  
    
    def left_child(self, i: int) -> int:  
        return 2 * i + 1  
    
    def right_child(self, i: int) -> int:  
        return 2 * i + 2  
    
    def push(self, value: T) -> None:  
        self.heap.append(value)  
        i = len(self.heap) - 1  
        while i > 0 and self.heap[i] < self.heap[self.parent(i)]:  
            self.heap[i], self.heap[self.parent(i)] = self.heap[self.parent(i)], self.heap[i]  
            i = self.parent(i)  
            
    def get_min(self) -> Optional[T]:  
        if len(self.heap) > 0:  
            return self.heap[0]  
        else:  
            return None  
    
    def pop(self) -> Optional[T]:  
        if len(self.heap) == 0:  
            return None  
        min_val = self.heap[0]  
        self.heap[0] = self.heap[-1]  
        self.heap.pop()  
        i = 0  
        while self.left_child(i) < len(self.heap):  
            child_index = self.left_child(i)  
            if self.right_child(i) < len(self.heap) and self.heap[self.right_child(i)] < self.heap[self.left_child(i)]:  
                child_index = self.right_child(i)  
            if self.heap[i] > self.heap[child_index]:  
                self.heap[i], self.heap[child_index] = self.heap[child_index], self.heap[i]  
                i = child_index  
            else:  
                break  
        return min_val  
    
    def build_heap(self, input_list: List[T]) -> None:  
        self.heap = input_list[:]  
        for i in range(len(self.heap) // 2, -1, -1):  
            self.min_heapify(i)  
  
    def min_heapify(self, i: int) -> None:  
        l = self.left_child(i)  
        r = self.right_child(i)  
        smallest = i  
        if l < len(self.heap) and self.heap[l] < self.heap[smallest]:  
            smallest = l  
        if r < len(self.heap) and self.heap[r] < self.heap[smallest]:  
            smallest = r  
        if smallest != i:  
            self.heap[i], self.heap[smallest] = self.heap[smallest], self.heap[i]  
            self.min_heapify(smallest)  
    
    def empty(self) -> bool:  
        return len(self.heap) == 0  
    
    def __len__(self) -> int:  
        return len(self.heap)
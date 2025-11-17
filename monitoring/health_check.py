"""Health check endpoints and system health monitoring"""
import time
import psutil
import os
from typing import Dict, Any, Optional, List, Callable
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
from threading import Lock


class HealthStatus(Enum):
    """Health status levels"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class ComponentHealth:
    """Represents the health of a component"""
    name: str
    status: HealthStatus
    message: str
    timestamp: datetime
    metadata: Dict[str, Any]


class HealthChecker:
    """System health checker"""
    
    def __init__(self):
        self._components: Dict[str, Callable[[], ComponentHealth]] = {}
        self._lock = Lock()
        self._start_time = datetime.utcnow()
        self._setup_default_checks()
    
    def _setup_default_checks(self):
        """Setup default health checks"""
        self.register_component('system', self._check_system_health)
        self.register_component('memory', self._check_memory_health)
        self.register_component('disk', self._check_disk_health)
        self.register_component('cpu', self._check_cpu_health)
    
    def register_component(self, name: str, check_func: Callable[[], ComponentHealth]) -> None:
        """Register a health check function for a component"""
        with self._lock:
            self._components[name] = check_func
    
    def unregister_component(self, name: str) -> None:
        """Unregister a health check"""
        with self._lock:
            if name in self._components:
                del self._components[name]
    
    def check_component(self, name: str) -> Optional[ComponentHealth]:
        """Check health of a specific component"""
        with self._lock:
            if name not in self._components:
                return None
        
        try:
            return self._components[name]()
        except Exception as e:
            return ComponentHealth(
                name=name,
                status=HealthStatus.UNHEALTHY,
                message=f"Health check failed: {str(e)}",
                timestamp=datetime.utcnow(),
                metadata={}
            )
    
    def check_health(self) -> Dict[str, Any]:
        """Check overall system health"""
        components = {}
        overall_status = HealthStatus.HEALTHY
        
        with self._lock:
            component_names = list(self._components.keys())
        
        for name in component_names:
            health = self.check_component(name)
            if health:
                components[name] = {
                    'status': health.status.value,
                    'message': health.message,
                    'timestamp': health.timestamp.isoformat(),
                    'metadata': health.metadata
                }
                
                # Determine overall status
                if health.status == HealthStatus.UNHEALTHY:
                    overall_status = HealthStatus.UNHEALTHY
                elif health.status == HealthStatus.DEGRADED and overall_status == HealthStatus.HEALTHY:
                    overall_status = HealthStatus.DEGRADED
        
        uptime_seconds = (datetime.utcnow() - self._start_time).total_seconds()
        
        return {
            'status': overall_status.value,
            'timestamp': datetime.utcnow().isoformat(),
            'uptime_seconds': uptime_seconds,
            'components': components
        }
    
    def _check_system_health(self) -> ComponentHealth:
        """Check basic system health"""
        return ComponentHealth(
            name='system',
            status=HealthStatus.HEALTHY,
            message='System is operational',
            timestamp=datetime.utcnow(),
            metadata={
                'uptime_seconds': (datetime.utcnow() - self._start_time).total_seconds()
            }
        )
    
    def _check_memory_health(self) -> ComponentHealth:
        """Check memory health"""
        try:
            process = psutil.Process(os.getpid())
            memory_percent = process.memory_percent()
            system_memory = psutil.virtual_memory()
            
            status = HealthStatus.HEALTHY
            message = 'Memory usage is normal'
            
            if memory_percent > 90 or system_memory.percent > 90:
                status = HealthStatus.UNHEALTHY
                message = 'Memory usage is critically high'
            elif memory_percent > 75 or system_memory.percent > 75:
                status = HealthStatus.DEGRADED
                message = 'Memory usage is elevated'
            
            return ComponentHealth(
                name='memory',
                status=status,
                message=message,
                timestamp=datetime.utcnow(),
                metadata={
                    'process_memory_percent': round(memory_percent, 2),
                    'system_memory_percent': round(system_memory.percent, 2),
                    'system_memory_available_gb': round(system_memory.available / 1024 / 1024 / 1024, 2)
                }
            )
        except Exception as e:
            return ComponentHealth(
                name='memory',
                status=HealthStatus.UNKNOWN,
                message=f'Could not check memory: {str(e)}',
                timestamp=datetime.utcnow(),
                metadata={}
            )
    
    def _check_disk_health(self) -> ComponentHealth:
        """Check disk health"""
        try:
            disk_usage = psutil.disk_usage('/')
            disk_percent = disk_usage.percent
            
            status = HealthStatus.HEALTHY
            message = 'Disk usage is normal'
            
            if disk_percent > 95:
                status = HealthStatus.UNHEALTHY
                message = 'Disk usage is critically high'
            elif disk_percent > 85:
                status = HealthStatus.DEGRADED
                message = 'Disk usage is elevated'
            
            return ComponentHealth(
                name='disk',
                status=status,
                message=message,
                timestamp=datetime.utcnow(),
                metadata={
                    'disk_percent': round(disk_percent, 2),
                    'disk_free_gb': round(disk_usage.free / 1024 / 1024 / 1024, 2),
                    'disk_total_gb': round(disk_usage.total / 1024 / 1024 / 1024, 2)
                }
            )
        except Exception as e:
            return ComponentHealth(
                name='disk',
                status=HealthStatus.UNKNOWN,
                message=f'Could not check disk: {str(e)}',
                timestamp=datetime.utcnow(),
                metadata={}
            )
    
    def _check_cpu_health(self) -> ComponentHealth:
        """Check CPU health"""
        try:
            process = psutil.Process(os.getpid())
            cpu_percent = process.cpu_percent(interval=0.1)
            system_cpu = psutil.cpu_percent(interval=0.1)
            
            status = HealthStatus.HEALTHY
            message = 'CPU usage is normal'
            
            if cpu_percent > 90 or system_cpu > 90:
                status = HealthStatus.UNHEALTHY
                message = 'CPU usage is critically high'
            elif cpu_percent > 75 or system_cpu > 75:
                status = HealthStatus.DEGRADED
                message = 'CPU usage is elevated'
            
            return ComponentHealth(
                name='cpu',
                status=status,
                message=message,
                timestamp=datetime.utcnow(),
                metadata={
                    'process_cpu_percent': round(cpu_percent, 2),
                    'system_cpu_percent': round(system_cpu, 2),
                    'cpu_count': psutil.cpu_count()
                }
            )
        except Exception as e:
            return ComponentHealth(
                name='cpu',
                status=HealthStatus.UNKNOWN,
                message=f'Could not check CPU: {str(e)}',
                timestamp=datetime.utcnow(),
                metadata={}
            )
    
    def is_ready(self) -> bool:
        """Check if system is ready (liveness probe)"""
        health = self.check_health()
        return health['status'] in ['healthy', 'degraded']
    
    def is_alive(self) -> bool:
        """Check if system is alive (readiness probe)"""
        return True  # Basic liveness check


# Global health checker instance
_health_checker: Optional[HealthChecker] = None


def get_health_checker() -> HealthChecker:
    """Get the global health checker instance"""
    global _health_checker
    if _health_checker is None:
        _health_checker = HealthChecker()
    return _health_checker



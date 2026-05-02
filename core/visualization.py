#!/usr/bin/env python3
"""
Data Visualization Engine for Akira Forge

Generate various data visualizations including charts, graphs,
dashboards, and interactive reports.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json
import logging

logger = logging.getLogger(__name__)


class ChartType(Enum):
    """Available chart types."""
    LINE = "line"
    BAR = "bar"
    PIE = "pie"
    SCATTER = "scatter"
    HISTOGRAM = "histogram"
    HEATMAP = "heatmap"
    BUBBLE = "bubble"


@dataclass
class ChartDataPoint:
    """Data point for chart."""
    label: str
    value: float
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ChartDataset:
    """Dataset for chart."""
    name: str
    data: List[ChartDataPoint]
    color: Optional[str] = None
    style: Optional[str] = None


@dataclass
class Chart:
    """Chart visualization."""
    chart_id: str
    title: str
    chart_type: ChartType
    datasets: List[ChartDataset] = field(default_factory=list)
    x_axis: Dict[str, Any] = field(default_factory=dict)
    y_axis: Dict[str, Any] = field(default_factory=dict)
    options: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'chart_id': self.chart_id,
            'title': self.title,
            'type': self.chart_type.value,
            'datasets': [
                {
                    'name': ds.name,
                    'data': [{'label': dp.label, 'value': dp.value} for dp in ds.data],
                    'color': ds.color
                }
                for ds in self.datasets
            ],
            'x_axis': self.x_axis,
            'y_axis': self.y_axis,
            'options': self.options
        }
    
    def to_json(self) -> str:
        """Convert to JSON."""
        return json.dumps(self.to_dict(), indent=2)


@dataclass
class Dashboard:
    """Interactive dashboard with multiple charts."""
    dashboard_id: str
    name: str
    description: str
    charts: List[Chart] = field(default_factory=list)
    refresh_interval: int = 300  # Seconds
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'dashboard_id': self.dashboard_id,
            'name': self.name,
            'description': self.description,
            'charts': [chart.to_dict() for chart in self.charts],
            'refresh_interval': self.refresh_interval,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class VisualizationEngine:
    """Generate data visualizations."""
    
    def __init__(self):
        self.charts = {}
        self.dashboards = {}
    
    def create_chart(self, title: str, chart_type: ChartType) -> Chart:
        """Create new chart."""
        import uuid
        chart_id = f"chart_{uuid.uuid4().hex[:8]}"
        
        chart = Chart(
            chart_id=chart_id,
            title=title,
            chart_type=chart_type
        )
        
        self.charts[chart_id] = chart
        logger.info(f"✓ Created chart: {title} ({chart_id})")
        return chart
    
    def add_dataset(self, chart_id: str, dataset: ChartDataset) -> bool:
        """Add dataset to chart."""
        if chart_id not in self.charts:
            return False
        
        self.charts[chart_id].datasets.append(dataset)
        self.charts[chart_id].updated_at = datetime.now()
        logger.info(f"✓ Added dataset to chart: {dataset.name}")
        return True
    
    def add_data_point(self, chart_id: str, dataset_name: str,
                      label: str, value: float,
                      metadata: Dict[str, Any] = None) -> bool:
        """Add data point to dataset."""
        if chart_id not in self.charts:
            return False
        
        chart = self.charts[chart_id]
        dataset = next(
            (ds for ds in chart.datasets if ds.name == dataset_name),
            None
        )
        
        if not dataset:
            return False
        
        point = ChartDataPoint(label, value, metadata or {})
        dataset.data.append(point)
        chart.updated_at = datetime.now()
        return True
    
    def create_dashboard(self, name: str, description: str = "") -> Dashboard:
        """Create new dashboard."""
        import uuid
        dashboard_id = f"dash_{uuid.uuid4().hex[:8]}"
        
        dashboard = Dashboard(
            dashboard_id=dashboard_id,
            name=name,
            description=description
        )
        
        self.dashboards[dashboard_id] = dashboard
        logger.info(f"✓ Created dashboard: {name} ({dashboard_id})")
        return dashboard
    
    def add_chart_to_dashboard(self, dashboard_id: str, chart_id: str) -> bool:
        """Add chart to dashboard."""
        if dashboard_id not in self.dashboards or chart_id not in self.charts:
            return False
        
        dashboard = self.dashboards[dashboard_id]
        chart = self.charts[chart_id]
        
        if chart not in dashboard.charts:
            dashboard.charts.append(chart)
            dashboard.updated_at = datetime.now()
            logger.info(f"✓ Added chart to dashboard: {chart.title}")
            return True
        
        return False
    
    def remove_chart_from_dashboard(self, dashboard_id: str, chart_id: str) -> bool:
        """Remove chart from dashboard."""
        if dashboard_id not in self.dashboards:
            return False
        
        dashboard = self.dashboards[dashboard_id]
        original_count = len(dashboard.charts)
        dashboard.charts = [c for c in dashboard.charts if c.chart_id != chart_id]
        
        if len(dashboard.charts) < original_count:
            dashboard.updated_at = datetime.now()
            logger.info(f"✓ Removed chart from dashboard")
            return True
        
        return False
    
    def generate_report(self, dashboard_id: str) -> Optional[str]:
        """Generate HTML report from dashboard."""
        if dashboard_id not in self.dashboards:
            return None
        
        dashboard = self.dashboards[dashboard_id]
        
        html = f"""
        <html>
        <head>
            <title>{dashboard.name} - Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .dashboard-header {{ 
                    background-color: #1f2937;
                    color: white;
                    padding: 20px;
                    border-radius: 8px;
                    margin-bottom: 20px;
                }}
                .dashboard-title {{ font-size: 24px; font-weight: bold; }}
                .dashboard-description {{ font-size: 14px; margin-top: 10px; opacity: 0.8; }}
                .charts-container {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(500px, 1fr)); gap: 20px; }}
                .chart-card {{
                    border: 1px solid #e5e7eb;
                    border-radius: 8px;
                    padding: 15px;
                    background: white;
                }}
                .chart-title {{ font-size: 16px; font-weight: bold; margin-bottom: 10px; }}
                .chart-data {{ background: #f3f4f6; padding: 10px; border-radius: 4px; font-family: monospace; }}
            </style>
        </head>
        <body>
            <div class="dashboard-header">
                <div class="dashboard-title">{dashboard.name}</div>
                <div class="dashboard-description">{dashboard.description}</div>
            </div>
            <div class="charts-container">
        """
        
        for chart in dashboard.charts:
            html += f"""
            <div class="chart-card">
                <div class="chart-title">{chart.title}</div>
                <div class="chart-data">
                    <strong>Type:</strong> {chart.chart_type.value}<br/>
                    <strong>Datasets:</strong> {len(chart.datasets)}<br/>
                    <strong>Data Points:</strong> {sum(len(ds.data) for ds in chart.datasets)}<br/>
                </div>
            </div>
            """
        
        html += """
            </div>
        </body>
        </html>
        """
        
        logger.info(f"✓ Generated report for dashboard: {dashboard.name}")
        return html
    
    def export_dashboard(self, dashboard_id: str, format: str = "json") -> Optional[str]:
        """Export dashboard in specified format."""
        if dashboard_id not in self.dashboards:
            return None
        
        dashboard = self.dashboards[dashboard_id]
        
        if format == "json":
            return dashboard.to_dict()
        elif format == "html":
            return self.generate_report(dashboard_id)
        
        return None
    
    def get_chart(self, chart_id: str) -> Optional[Chart]:
        """Get chart by ID."""
        return self.charts.get(chart_id)
    
    def get_dashboard(self, dashboard_id: str) -> Optional[Dashboard]:
        """Get dashboard by ID."""
        return self.dashboards.get(dashboard_id)
    
    def list_charts(self) -> List[Chart]:
        """List all charts."""
        return list(self.charts.values())
    
    def list_dashboards(self) -> List[Dashboard]:
        """List all dashboards."""
        return list(self.dashboards.values())
    
    def get_chart_statistics(self, chart_id: str) -> Dict[str, Any]:
        """Get chart statistics."""
        if chart_id not in self.charts:
            return {}
        
        chart = self.charts[chart_id]
        all_values = []
        for dataset in chart.datasets:
            all_values.extend([dp.value for dp in dataset.data])
        
        if not all_values:
            return {}
        
        return {
            'chart_id': chart_id,
            'title': chart.title,
            'type': chart.chart_type.value,
            'datasets_count': len(chart.datasets),
            'data_points_count': len(all_values),
            'min_value': min(all_values),
            'max_value': max(all_values),
            'avg_value': sum(all_values) / len(all_values),
            'total_value': sum(all_values)
        }


# Global instance
_engine = None


def get_visualization_engine() -> VisualizationEngine:
    """Get or create visualization engine."""
    global _engine
    if _engine is None:
        _engine = VisualizationEngine()
    return _engine

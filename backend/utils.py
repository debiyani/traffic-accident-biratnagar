"""
Utilities for the backend
"""

import json
import base64
from io import BytesIO
import matplotlib.pyplot as plt


def create_pie_chart_data(labels, sizes, colors=None):
    """
    Create pie chart data as base64 encoded image
    
    Args:
        labels: list of labels
        sizes: list of values
        colors: optional list of colors
    
    Returns:
        base64 encoded image string
    """
    try:
        fig, ax = plt.subplots(figsize=(8, 6))
        
        if colors:
            ax.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors, startangle=90)
        else:
            ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90)
        
        ax.axis('equal')
        
        # Convert to base64
        buffer = BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close(fig)
        
        return f'data:image/png;base64,{image_base64}'
    
    except Exception as e:
        return None


def create_bar_chart_data(labels, values, title='', xlabel='', ylabel=''):
    """
    Create bar chart data as base64 encoded image
    
    Args:
        labels: list of labels
        values: list of values
        title: chart title
        xlabel: x-axis label
        ylabel: y-axis label
    
    Returns:
        base64 encoded image string
    """
    try:
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(labels, values)
        ax.set_title(title)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        plt.xticks(rotation=45, ha='right')
        
        # Convert to base64
        buffer = BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close(fig)
        
        return f'data:image/png;base64,{image_base64}'
    
    except Exception as e:
        return None


def format_response(data, success=True, message=''):
    """
    Format response with metadata
    
    Args:
        data: response data
        success: boolean
        message: optional message
    
    Returns:
        formatted response dict
    """
    return {
        'success': success,
        'message': message,
        'data': data
    }

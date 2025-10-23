"""
Database Models for Network Flow Storage

Stores network flow features for:
- Historical analysis
- Model retraining
- Anomaly detection improvement
- Attack pattern analysis
"""

from sqlalchemy import (
    Column, Integer, Float, String, DateTime, Boolean,
    Text, Index, create_engine
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import json

Base = declarative_base()


class NetworkFlow(Base):
    """
    Table to store network flow features (46 features from CICIoT2023)
    Each row represents one network flow with all extracted features
    """
    __tablename__ = 'network_flows'

    # Primary identification
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Flow identification
    src_ip = Column(String(45), nullable=False, index=True)  # IPv4 or IPv6
    dst_ip = Column(String(45), nullable=False, index=True)
    src_port = Column(Integer, nullable=True)
    dst_port = Column(Integer, nullable=True)
    protocol = Column(Integer, nullable=False)  # 6=TCP, 17=UDP, etc.

    # === CICIoT2023 Features (46 total) ===

    # Time-based features
    flow_duration = Column(Float, nullable=False)
    Duration = Column(Float, nullable=False)

    # Header features
    Header_Length = Column(Float, nullable=False)
    Protocol_Type = Column(Integer, nullable=False)

    # Rate features
    Rate = Column(Float, nullable=True)
    Srate = Column(Float, nullable=True)  # No longer used by retrained model
    Drate = Column(Float, nullable=True)

    # TCP flag counts
    fin_flag_number = Column(Integer, default=0)
    syn_flag_number = Column(Integer, default=0)
    rst_flag_number = Column(Integer, default=0, nullable=True) # No longer used
    psh_flag_number = Column(Integer, default=0)
    ack_flag_number = Column(Integer, default=0)
    ece_flag_number = Column(Integer, default=0)
    cwr_flag_number = Column(Integer, default=0)
    ack_count = Column(Integer, default=0, nullable=True) # No longer used
    syn_count = Column(Integer, default=0)
    fin_count = Column(Integer, default=0)
    urg_count = Column(Integer, default=0)
    rst_count = Column(Integer, default=0)

    # Protocol indicators (binary 0/1)
    HTTP = Column(Integer, default=0)
    HTTPS = Column(Integer, default=0)
    DNS = Column(Integer, default=0)
    Telnet = Column(Integer, default=0)
    SMTP = Column(Integer, default=0)
    SSH = Column(Integer, default=0)
    IRC = Column(Integer, default=0)
    TCP = Column(Integer, default=0)
    UDP = Column(Integer, default=0)
    DHCP = Column(Integer, default=0)
    ARP = Column(Integer, default=0)
    ICMP = Column(Integer, default=0)
    IPv = Column(Integer, default=0)
    LLC = Column(Integer, default=0, nullable=True) # No longer used

    # Statistical features
    Tot_sum = Column(Float, nullable=True)
    Min = Column(Float, nullable=True)
    Max = Column(Float, nullable=True)
    AVG = Column(Float, nullable=True)
    Std = Column(Float, nullable=True) # No longer used
    Tot_size = Column(Float, nullable=True)
    IAT = Column(Float, nullable=True)  # Inter-arrival time
    Number = Column(Integer, nullable=True)  # No longer used

    # Advanced features
    Magnitue = Column(Float, nullable=True)  # No longer used
    Radius = Column(Float, nullable=True)  # No longer used
    Covariance = Column(Float, nullable=True)
    Variance = Column(Float, nullable=True)
    Weight = Column(Float, nullable=True)  # No longer used

    # === Prediction Results ===
    predicted_attack = Column(String(100), nullable=True)
    predicted_severity = Column(String(20), nullable=True)
    confidence = Column(Float, nullable=True)
    is_anomaly = Column(Boolean, default=False)
    anomaly_score = Column(Float, nullable=True)

    # Label (for supervised learning)
    label = Column(String(100), nullable=True)  # Ground truth if known
    label_verified = Column(Boolean, default=False)

    # Metadata
    detection_method = Column(String(50), nullable=True)  # ml, dl, ensemble
    alert_generated = Column(Boolean, default=False)
    notes = Column(Text, nullable=True)

    # Indexes for common queries
    __table_args__ = (
        Index('idx_timestamp_attack', 'timestamp', 'predicted_attack'),
        Index('idx_src_dst', 'src_ip', 'dst_ip'),
        Index('idx_anomaly', 'is_anomaly', 'timestamp'),
        Index('idx_label', 'label'),
    )

    def to_dict(self):
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'src_ip': self.src_ip,
            'dst_ip': self.dst_ip,
            'src_port': self.src_port,
            'dst_port': self.dst_port,
            'protocol': self.protocol,
            'predicted_attack': self.predicted_attack,
            'confidence': self.confidence,
            'is_anomaly': self.is_anomaly,
        }

    def get_features_dict(self):
        """Get the 37 features used by the retrained model as a dictionary."""
        return {
            'flow_duration': self.flow_duration,
            'Header_Length': self.Header_Length,
            'Protocol Type': self.Protocol_Type,
            'Duration': self.Duration,
            'Rate': self.Rate,
            'Drate': self.Drate,
            'fin_flag_number': self.fin_flag_number,
            'syn_flag_number': self.syn_flag_number,
            'psh_flag_number': self.psh_flag_number,
            'ack_flag_number': self.ack_flag_number,
            'ece_flag_number': self.ece_flag_number,
            'cwr_flag_number': self.cwr_flag_number,
            'syn_count': self.syn_count,
            'fin_count': self.fin_count,
            'urg_count': self.urg_count,
            'rst_count': self.rst_count,
            'HTTP': self.HTTP,
            'HTTPS': self.HTTPS,
            'DNS': self.DNS,
            'Telnet': self.Telnet,
            'SMTP': self.SMTP,
            'SSH': self.SSH,
            'IRC': self.IRC,
            'TCP': self.TCP,
            'UDP': self.UDP,
            'DHCP': self.DHCP,
            'ARP': self.ARP,
            'ICMP': self.ICMP,
            'IPv': self.IPv,
            'Tot sum': self.Tot_sum,
            'Min': self.Min,
            'Max': self.Max,
            'AVG': self.AVG,
            'Tot size': self.Tot_size,
            'IAT': self.IAT,
            'Covariance': self.Covariance,
            'Variance': self.Variance,
        }


class ModelTrainingMetadata(Base):
    """
    Track model training sessions and performance
    """
    __tablename__ = 'model_training_metadata'

    id = Column(Integer, primary_key=True, autoincrement=True)
    training_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    model_type = Column(String(50), nullable=False)  # xgboost, ffnn, autoencoder
    model_path = Column(String(500), nullable=False)

    # Training data info
    training_samples = Column(Integer, nullable=False)
    test_samples = Column(Integer, nullable=False)
    feature_count = Column(Integer, nullable=False)

    # Performance metrics (JSON)
    metrics = Column(Text, nullable=True)  # Store as JSON string

    # Hyperparameters (JSON)
    hyperparameters = Column(Text, nullable=True)

    # Status
    is_active = Column(Boolean, default=True)
    notes = Column(Text, nullable=True)

    def get_metrics(self):
        """Parse metrics JSON"""
        if self.metrics:
            return json.loads(self.metrics)
        return {}

    def set_metrics(self, metrics_dict):
        """Store metrics as JSON"""
        self.metrics = json.dumps(metrics_dict)


class DatasetExport(Base):
    """
    Track dataset exports for model training
    """
    __tablename__ = 'dataset_exports'

    id = Column(Integer, primary_key=True, autoincrement=True)
    export_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    export_path = Column(String(500), nullable=False)

    # Export parameters
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    record_count = Column(Integer, nullable=False)

    # Filters applied
    include_benign = Column(Boolean, default=True)
    include_attacks = Column(Boolean, default=True)
    attack_types = Column(Text, nullable=True)  # JSON list

    # Format
    export_format = Column(String(20), default='csv')  # csv, parquet, json

    notes = Column(Text, nullable=True)

"""
Database Manager for Network Flow Storage

Handles database connections, CRUD operations, and data export for model training.
Supports both SQLite (development) and PostgreSQL (production).
"""

import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Union
import pandas as pd
from sqlalchemy import create_engine, and_, or_, desc
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from contextlib import contextmanager

from src.database.models import Base, NetworkFlow, ModelTrainingMetadata, DatasetExport

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages database operations for network flow storage"""

    def __init__(self, db_url: str = None, db_dir: str = "data/flows"):
        """
        Initialize database manager.

        Args:
            db_url: Database URL (SQLite or PostgreSQL)
                   Format:
                   - SQLite: "sqlite:///path/to/db.sqlite"
                   - PostgreSQL: "postgresql://user:pass@host:port/dbname"
            db_dir: Directory for SQLite database (default: data/flows)
        """
        if db_url is None:
            # Default to SQLite in data/flows directory
            db_path = Path(db_dir)
            db_path.mkdir(parents=True, exist_ok=True)
            db_file = db_path / "network_flows.sqlite"
            db_url = f"sqlite:///{db_file}"

        self.db_url = db_url
        self.engine = self._create_engine(db_url)
        self.SessionLocal = sessionmaker(bind=self.engine, expire_on_commit=False)

        # Create tables if they don't exist
        self._init_db()

        logger.info(f"Database initialized: {db_url}")

    def _create_engine(self, db_url: str):
        """Create SQLAlchemy engine with appropriate settings"""
        if db_url.startswith('sqlite'):
            # SQLite settings
            return create_engine(
                db_url,
                connect_args={'check_same_thread': False},
                poolclass=StaticPool,
                echo=False
            )
        else:
            # PostgreSQL settings
            return create_engine(
                db_url,
                pool_size=10,
                max_overflow=20,
                pool_pre_ping=True,
                echo=False
            )

    def _init_db(self):
        """Create all tables"""
        Base.metadata.create_all(bind=self.engine)
        logger.info("Database tables created/verified")

    @contextmanager
    def get_session(self) -> Session:
        """Context manager for database sessions"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()

    # === Network Flow Operations ===

    def save_flow(
        self,
        features_df: pd.DataFrame,
        src_ip: str,
        dst_ip: str,
        protocol: int,
        src_port: int = None,
        dst_port: int = None,
        prediction: Dict = None
    ) -> int:
        """
        Save a network flow with its features.

        Args:
            features_df: DataFrame with model features (single row)
            src_ip: Source IP address
            dst_ip: Destination IP address
            protocol: Protocol number (6=TCP, 17=UDP, etc.)
            src_port: Source port (optional)
            dst_port: Destination port (optional)
            prediction: Prediction results dict (optional)

        Returns:
            flow_id: ID of saved flow
        """
        try:
            # Extract features from DataFrame
            if features_df.empty:
                logger.warning("Empty features DataFrame, skipping save")
                return None

            features = features_df.iloc[0].to_dict()

            # Create flow object
            flow = NetworkFlow(
                timestamp=datetime.utcnow(),
                src_ip=src_ip,
                dst_ip=dst_ip,
                src_port=src_port,
                dst_port=dst_port,
                protocol=protocol,
                # Assign all available features from the dataframe
                flow_duration=float(features.get('flow_duration', 0)),
                Header_Length=float(features.get('Header_Length', 0)),
                Protocol_Type=int(features.get('Protocol Type', protocol)),
                Duration=float(features.get('Duration', 0)),
                Rate=float(features.get('Rate', 0)),
                Srate=float(features.get('Srate')) if 'Srate' in features else None,
                Drate=float(features.get('Drate', 0)),
                fin_flag_number=int(features.get('fin_flag_number', 0)),
                syn_flag_number=int(features.get('syn_flag_number', 0)),
                rst_flag_number=int(features.get('rst_flag_number')) if 'rst_flag_number' in features else None,
                psh_flag_number=int(features.get('psh_flag_number', 0)),
                ack_flag_number=int(features.get('ack_flag_number', 0)),
                ece_flag_number=int(features.get('ece_flag_number', 0)),
                cwr_flag_number=int(features.get('cwr_flag_number', 0)),
                ack_count=int(features.get('ack_count')) if 'ack_count' in features else None,
                syn_count=int(features.get('syn_count', 0)),
                fin_count=int(features.get('fin_count', 0)),
                urg_count=int(features.get('urg_count', 0)),
                rst_count=int(features.get('rst_count', 0)),
                HTTP=int(features.get('HTTP', 0)),
                HTTPS=int(features.get('HTTPS', 0)),
                DNS=int(features.get('DNS', 0)),
                Telnet=int(features.get('Telnet', 0)),
                SMTP=int(features.get('SMTP', 0)),
                SSH=int(features.get('SSH', 0)),
                IRC=int(features.get('IRC', 0)),
                TCP=int(features.get('TCP', 0)),
                UDP=int(features.get('UDP', 0)),
                DHCP=int(features.get('DHCP', 0)),
                ARP=int(features.get('ARP', 0)),
                ICMP=int(features.get('ICMP', 0)),
                IPv=int(features.get('IPv', 0)),
                LLC=int(features.get('LLC')) if 'LLC' in features else None,
                Tot_sum=float(features.get('Tot sum', 0)),
                Min=float(features.get('Min', 0)),
                Max=float(features.get('Max', 0)),
                AVG=float(features.get('AVG', 0)),
                Std=float(features.get('Std')) if 'Std' in features else None,
                Tot_size=float(features.get('Tot size', 0)),
                IAT=float(features.get('IAT', 0)),
                Number=int(features.get('Number')) if 'Number' in features else None,
                Magnitue=float(features.get('Magnitue')) if 'Magnitue' in features else None,
                Radius=float(features.get('Radius')) if 'Radius' in features else None,
                Covariance=float(features.get('Covariance', 0)),
                Variance=float(features.get('Variance', 0)),
                Weight=float(features.get('Weight')) if 'Weight' in features else None
            )

            # Add prediction results if provided
            if prediction:
                flow.predicted_attack = prediction.get('attack')
                flow.predicted_severity = prediction.get('severity')
                flow.confidence = prediction.get('confidence')
                flow.detection_method = prediction.get('method')

                anomaly = prediction.get('anomaly', {})
                flow.is_anomaly = anomaly.get('is_anomaly', False)
                flow.anomaly_score = anomaly.get('mse_normalized')

            # Save to database
            with self.get_session() as session:
                session.add(flow)
                session.flush()
                flow_id = flow.id

            logger.debug(f"Saved flow {flow_id}: {src_ip}:{src_port} -> {dst_ip}:{dst_port}")
            return flow_id

        except Exception as e:
            logger.error(f"Failed to save flow: {e}")
            return None

    def get_flow(self, flow_id: int) -> Optional[NetworkFlow]:
        """Get a flow by ID"""
        with self.get_session() as session:
            return session.query(NetworkFlow).filter(NetworkFlow.id == flow_id).first()

    def get_recent_flows(self, limit: int = 100, hours: int = 24) -> List[NetworkFlow]:
        """
        Get recent flows.

        Args:
            limit: Maximum number of flows to return
            hours: Only include flows from last N hours

        Returns:
            List of NetworkFlow objects
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)

        with self.get_session() as session:
            flows = session.query(NetworkFlow)\
                .filter(NetworkFlow.timestamp >= cutoff_time)\
                .order_by(desc(NetworkFlow.timestamp))\
                .limit(limit)\
                .all()

            # Detach from session
            session.expunge_all()
            return flows

    def get_flows_by_attack_type(
        self,
        attack_type: str,
        limit: int = 1000,
        start_date: datetime = None,
        end_date: datetime = None
    ) -> List[NetworkFlow]:
        """Get flows by attack type"""
        with self.get_session() as session:
            query = session.query(NetworkFlow)\
                .filter(NetworkFlow.predicted_attack == attack_type)

            if start_date:
                query = query.filter(NetworkFlow.timestamp >= start_date)
            if end_date:
                query = query.filter(NetworkFlow.timestamp <= end_date)

            flows = query.order_by(desc(NetworkFlow.timestamp)).limit(limit).all()
            session.expunge_all()
            return flows

    def get_anomalies(
        self,
        limit: int = 100,
        min_score: float = 1.0,
        hours: int = 24
    ) -> List[NetworkFlow]:
        """Get anomalous flows"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)

        with self.get_session() as session:
            flows = session.query(NetworkFlow)\
                .filter(NetworkFlow.is_anomaly == True)\
                .filter(NetworkFlow.anomaly_score >= min_score)\
                .filter(NetworkFlow.timestamp >= cutoff_time)\
                .order_by(desc(NetworkFlow.timestamp))\
                .limit(limit)\
                .all()

            session.expunge_all()
            return flows

    def update_flow_label(self, flow_id: int, label: str, verified: bool = True):
        """Update ground truth label for a flow (for supervised learning)"""
        with self.get_session() as session:
            flow = session.query(NetworkFlow).filter(NetworkFlow.id == flow_id).first()
            if flow:
                flow.label = label
                flow.label_verified = verified
                logger.info(f"Updated label for flow {flow_id}: {label}")

    def get_flow_count(self, attack_type: str = None, hours: int = 24) -> int:
        """Get count of flows"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)

        with self.get_session() as session:
            query = session.query(NetworkFlow).filter(NetworkFlow.timestamp >= cutoff_time)

            if attack_type:
                query = query.filter(NetworkFlow.predicted_attack == attack_type)

            return query.count()

    def get_statistics(self, hours: int = 24) -> Dict:
        """Get database statistics"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)

        with self.get_session() as session:
            total_flows = session.query(NetworkFlow)\
                .filter(NetworkFlow.timestamp >= cutoff_time).count()

            attack_flows = session.query(NetworkFlow)\
                .filter(NetworkFlow.timestamp >= cutoff_time)\
                .filter(NetworkFlow.predicted_attack != 'BENIGN').count()

            anomalies = session.query(NetworkFlow)\
                .filter(NetworkFlow.timestamp >= cutoff_time)\
                .filter(NetworkFlow.is_anomaly == True).count()

            return {
                'total_flows': total_flows,
                'attack_flows': attack_flows,
                'benign_flows': total_flows - attack_flows,
                'anomalies': anomalies,
                'time_window_hours': hours
            }

    # === Export Operations ===

    def export_to_csv(
        self,
        output_path: str,
        start_date: datetime = None,
        end_date: datetime = None,
        attack_types: List[str] = None,
        include_benign: bool = True,
        include_predictions: bool = True
    ) -> int:
        """
        Export flows to CSV for model training.

        Args:
            output_path: Path to save CSV file
            start_date: Start date filter (optional)
            end_date: End date filter (optional)
            attack_types: List of attack types to include (optional)
            include_benign: Include benign flows (default: True)
            include_predictions: Include prediction columns (default: True)

        Returns:
            Number of records exported
        """
        with self.get_session() as session:
            query = session.query(NetworkFlow)

            # Apply filters
            if start_date:
                query = query.filter(NetworkFlow.timestamp >= start_date)
            if end_date:
                query = query.filter(NetworkFlow.timestamp <= end_date)

            if attack_types:
                if include_benign:
                    query = query.filter(
                        or_(
                            NetworkFlow.predicted_attack.in_(attack_types),
                            NetworkFlow.predicted_attack == 'BENIGN'
                        )
                    )
                else:
                    query = query.filter(NetworkFlow.predicted_attack.in_(attack_types))
            elif not include_benign:
                query = query.filter(NetworkFlow.predicted_attack != 'BENIGN')

            # Fetch all flows
            flows = query.all()

            if not flows:
                logger.warning("No flows to export")
                return 0

            # Convert to DataFrame
            data = []
            for flow in flows:
                row = flow.get_features_dict()

                # Add metadata
                row['timestamp'] = flow.timestamp
                row['src_ip'] = flow.src_ip
                row['dst_ip'] = flow.dst_ip
                row['src_port'] = flow.src_port
                row['dst_port'] = flow.dst_port

                if include_predictions:
                    row['predicted_attack'] = flow.predicted_attack
                    row['predicted_severity'] = flow.predicted_severity
                    row['confidence'] = flow.confidence
                    row['is_anomaly'] = flow.is_anomaly
                    row['anomaly_score'] = flow.anomaly_score

                # Add label if available
                if flow.label:
                    row['label'] = flow.label
                    row['label_verified'] = flow.label_verified

                data.append(row)

            df = pd.DataFrame(data)

            # Save to CSV
            df.to_csv(output_path, index=False)
            record_count = len(df)

            # Record export
            export = DatasetExport(
                export_date=datetime.utcnow(),
                export_path=output_path,
                start_date=start_date,
                end_date=end_date,
                record_count=record_count,
                include_benign=include_benign,
                include_attacks=(attack_types is None or len(attack_types) > 0),
                attack_types=str(attack_types) if attack_types else None,
                export_format='csv'
            )
            session.add(export)

            logger.info(f"Exported {record_count} flows to {output_path}")
            return record_count

    def export_to_dataframe(
        self,
        start_date: datetime = None,
        end_date: datetime = None,
        features_only: bool = False
    ) -> pd.DataFrame:
        """
        Export flows to pandas DataFrame.

        Args:
            start_date: Start date filter (optional)
            end_date: End date filter (optional)
            features_only: Return only 46 features (default: False)

        Returns:
            DataFrame with flows
        """
        with self.get_session() as session:
            query = session.query(NetworkFlow)

            if start_date:
                query = query.filter(NetworkFlow.timestamp >= start_date)
            if end_date:
                query = query.filter(NetworkFlow.timestamp <= end_date)

            flows = query.all()

            if not flows:
                return pd.DataFrame()

            if features_only:
                data = [flow.get_features_dict() for flow in flows]
            else:
                data = []
                for flow in flows:
                    row = flow.get_features_dict()
                    row.update({
                        'timestamp': flow.timestamp,
                        'src_ip': flow.src_ip,
                        'dst_ip': flow.dst_ip,
                        'predicted_attack': flow.predicted_attack,
                        'confidence': flow.confidence,
                        'is_anomaly': flow.is_anomaly,
                    })
                    data.append(row)

            return pd.DataFrame(data)

    def cleanup_old_flows(self, days: int = 30) -> int:
        """
        Delete flows older than specified days.

        Args:
            days: Delete flows older than N days

        Returns:
            Number of deleted flows
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        with self.get_session() as session:
            deleted = session.query(NetworkFlow)\
                .filter(NetworkFlow.timestamp < cutoff_date)\
                .delete()

            logger.info(f"Deleted {deleted} flows older than {days} days")
            return deleted

"""
Data Export Utilities for Model Training

Tools to export database flows for model training and retraining.
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.database.db_manager import DatabaseManager


def export_for_training(
    output_path: str,
    days: int = 30,
    attack_types: list = None,
    include_benign: bool = True,
    min_confidence: float = 0.8,
    db_path: str = None
):
    """
    Export database flows to CSV for model training.

    Args:
        output_path: Path to save CSV file
        days: Export data from last N days
        attack_types: List of specific attack types to include
        include_benign: Include benign flows (default: True)
        min_confidence: Minimum confidence threshold for predictions
        db_path: Custom database path (optional)

    Returns:
        Number of records exported
    """
    # Initialize database manager
    if db_path:
        db_manager = DatabaseManager(db_url=f"sqlite:///{db_path}")
    else:
        db_manager = DatabaseManager()

    # Calculate date range
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)

    print(f"Exporting flows from {start_date} to {end_date}")
    print(f"Attack types: {attack_types if attack_types else 'All'}")
    print(f"Include benign: {include_benign}")
    print(f"Min confidence: {min_confidence}")

    # Export to CSV
    count = db_manager.export_to_csv(
        output_path=output_path,
        start_date=start_date,
        end_date=end_date,
        attack_types=attack_types,
        include_benign=include_benign,
        include_predictions=True
    )

    # Filter by confidence if specified
    if min_confidence > 0:
        print(f"\nFiltering by confidence >= {min_confidence}")
        df = pd.read_csv(output_path)
        original_count = len(df)

        # Keep flows with high confidence or no prediction (for labeling)
        df_filtered = df[(df['confidence'] >= min_confidence) | (df['confidence'].isna())]

        df_filtered.to_csv(output_path, index=False)
        filtered_count = len(df_filtered)
        print(f"Kept {filtered_count}/{original_count} flows after confidence filtering")
        count = filtered_count

    print(f"\n[OK] Exported {count} flows to {output_path}")
    return count


def export_attack_samples(
    output_dir: str,
    min_samples_per_class: int = 100,
    days: int = 30,
    db_path: str = None
):
    """
    Export balanced samples for each attack type.

    Args:
        output_dir: Directory to save CSV files
        min_samples_per_class: Minimum samples per attack type
        days: Export data from last N days
        db_path: Custom database path (optional)

    Returns:
        Dictionary with attack types and sample counts
    """
    # Initialize database manager
    if db_path:
        db_manager = DatabaseManager(db_url=f"sqlite:///{db_path}")
    else:
        db_manager = DatabaseManager()

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Calculate date range
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)

    # Get all flows
    df = db_manager.export_to_dataframe(start_date=start_date, end_date=end_date)

    if df.empty:
        print("[!] No flows found in database")
        return {}

    print(f"Total flows in database: {len(df)}")

    # Group by attack type
    attack_counts = df['predicted_attack'].value_counts()
    print("\nAttack type distribution:")
    for attack, count in attack_counts.items():
        print(f"  {attack}: {count}")

    # Export each attack type
    results = {}
    for attack_type in attack_counts.index:
        attack_df = df[df['predicted_attack'] == attack_type]

        if len(attack_df) >= min_samples_per_class:
            # Save to separate CSV
            filename = output_path / f"{attack_type.lower().replace(' ', '_')}_samples.csv"
            attack_df.to_csv(filename, index=False)
            results[attack_type] = len(attack_df)
            print(f"[OK] Saved {len(attack_df)} samples of {attack_type} to {filename}")
        else:
            print(f"[SKIP] {attack_type}: Only {len(attack_df)} samples (need {min_samples_per_class})")

    return results


def export_labeled_data(
    output_path: str,
    only_verified: bool = True,
    db_path: str = None
):
    """
    Export flows with ground truth labels for supervised learning.

    Args:
        output_path: Path to save CSV file
        only_verified: Only export verified labels (default: True)
        db_path: Custom database path (optional)

    Returns:
        Number of records exported
    """
    # Initialize database manager
    if db_path:
        db_manager = DatabaseManager(db_url=f"sqlite:///{db_path}")
    else:
        db_manager = DatabaseManager()

    # Get all flows with labels
    with db_manager.get_session() as session:
        from src.database.models import NetworkFlow

        query = session.query(NetworkFlow).filter(NetworkFlow.label.isnot(None))

        if only_verified:
            query = query.filter(NetworkFlow.label_verified == True)

        flows = query.all()

        if not flows:
            print("[!] No labeled flows found in database")
            return 0

        # Convert to DataFrame
        data = []
        for flow in flows:
            row = flow.get_features_dict()
            row['label'] = flow.label
            row['label_verified'] = flow.label_verified
            row['predicted_attack'] = flow.predicted_attack
            row['confidence'] = flow.confidence
            row['timestamp'] = flow.timestamp
            data.append(row)

        df = pd.DataFrame(data)

        # Save to CSV
        df.to_csv(output_path, index=False)

        print(f"[OK] Exported {len(df)} labeled flows to {output_path}")

        # Show label distribution
        print("\nLabel distribution:")
        for label, count in df['label'].value_counts().items():
            print(f"  {label}: {count}")

        return len(df)


def main():
    """Command-line interface for data export"""
    parser = argparse.ArgumentParser(description='Export network flow data for model training')

    subparsers = parser.add_subparsers(dest='command', help='Export command')

    # Export for training
    train_parser = subparsers.add_parser('train', help='Export data for model training')
    train_parser.add_argument('--output', '-o', required=True, help='Output CSV path')
    train_parser.add_argument('--days', '-d', type=int, default=30, help='Export last N days (default: 30)')
    train_parser.add_argument('--attacks', '-a', nargs='+', help='Specific attack types to include')
    train_parser.add_argument('--no-benign', action='store_true', help='Exclude benign flows')
    train_parser.add_argument('--min-confidence', type=float, default=0.8, help='Minimum confidence (default: 0.8)')
    train_parser.add_argument('--db', help='Custom database path')

    # Export attack samples
    samples_parser = subparsers.add_parser('samples', help='Export balanced samples per attack type')
    samples_parser.add_argument('--output-dir', '-o', required=True, help='Output directory')
    samples_parser.add_argument('--min-samples', type=int, default=100, help='Min samples per class (default: 100)')
    samples_parser.add_argument('--days', '-d', type=int, default=30, help='Export last N days (default: 30)')
    samples_parser.add_argument('--db', help='Custom database path')

    # Export labeled data
    label_parser = subparsers.add_parser('labels', help='Export labeled data for supervised learning')
    label_parser.add_argument('--output', '-o', required=True, help='Output CSV path')
    label_parser.add_argument('--include-unverified', action='store_true', help='Include unverified labels')
    label_parser.add_argument('--db', help='Custom database path')

    args = parser.parse_args()

    if args.command == 'train':
        export_for_training(
            output_path=args.output,
            days=args.days,
            attack_types=args.attacks,
            include_benign=not args.no_benign,
            min_confidence=args.min_confidence,
            db_path=args.db
        )

    elif args.command == 'samples':
        export_attack_samples(
            output_dir=args.output_dir,
            min_samples_per_class=args.min_samples,
            days=args.days,
            db_path=args.db
        )

    elif args.command == 'labels':
        export_labeled_data(
            output_path=args.output,
            only_verified=not args.include_unverified,
            db_path=args.db
        )

    else:
        parser.print_help()


if __name__ == '__main__':
    main()

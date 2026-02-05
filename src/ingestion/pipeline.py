"""Main data ingestion pipeline orchestrator"""
import yaml
import logging
from pathlib import Path
from .loader import DataLoader
from .validator import SchemaValidator
from .profiler import DataProfiler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class DataIngestionPipeline:
    """Main data ingestion orchestrator"""
    
    def __init__(self, config_path: str = "src/config/config.yaml"):
        """Initialize pipeline with configuration"""
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.loader = DataLoader(self.config)
        self.validator = SchemaValidator(self.config)
        self.profiler = DataProfiler(self.config)
    
    def run(self):
        """Execute full ingestion pipeline"""
        logger.info("=" * 70)
        logger.info("STARTING DATA INGESTION PIPELINE FOR FRAUD DETECTION")
        logger.info("=" * 70)
        
        try:
            # Step 1: Load data
            logger.info("\n[STEP 1/5] Loading data from source...")
            df = self.loader.load_csv()
            
            # Step 2: Validate schema
            logger.info("\n[STEP 2/5] Validating data schema...")
            schema_valid, schema_errors = self.validator.validate_schema(df)
            if not schema_valid:
                logger.error("âŒ Schema validation failed!")
                raise ValueError(f"Schema errors: {schema_errors}")
            
            # Step 3: Validate quality
            logger.info("\n[STEP 3/5] Running data quality checks...")
            quality_valid, quality_report = self.validator.validate_quality(df)
            self._log_quality_report(quality_report)
            
            # Step 4: Profile data
            logger.info("\n[STEP 4/5] Profiling data...")
            profile = self.profiler.profile(df)
            profile_path = self.config['data']['profile_path']
            self.profiler.save_profile(profile, profile_path)
            
            # Step 5: Save validated data
            logger.info("\n[STEP 5/5] Saving validated data in Parquet format...")
            output_path = self.config['data']['validated_path']
            self.loader.save_parquet(df, output_path)
            
            logger.info("\n" + "=" * 70)
            logger.info("âœ… DATA INGESTION PIPELINE COMPLETED SUCCESSFULLY!")
            logger.info("=" * 70)
            logger.info(f"\nOutput Location: {output_path}")
            logger.info(f"Profile Location: {profile_path}")
            
            return df
        
        except Exception as e:
            logger.error(f"\nâŒ Pipeline failed with error: {e}")
            raise
    
    def _log_quality_report(self, report: dict) -> None:
        """Pretty print quality report"""
        logger.info("\nðŸ“Š DATA QUALITY REPORT:")
        logger.info(f"   Total Rows: {report['total_rows']:,}")
        logger.info(f"   Total Columns: {report['total_columns']}")
        
        checks = report['checks']
        logger.info("\n   Quality Checks:")
        
        if 'minimum_rows' in checks:
            c = checks['minimum_rows']
            status = "âœ“" if c['passed'] else "âœ—"
            logger.info(f"     {status} Minimum Rows: {c['value']:,} (threshold: {c['threshold']:,})")
        
        if 'completeness' in checks:
            c = checks['completeness']
            status = "âœ“" if c['passed'] else "âœ—"
            logger.info(f"     {status} Completeness: {c['value']:.2%} (threshold: {c['threshold']:.2%})")
        
        if 'duplicates' in checks:
            d = checks['duplicates']
            status = "âœ“" if d['passed'] else "âœ—"
            logger.info(f"     {status} Duplicates: {d['value']:.4%} (threshold: {d['threshold']:.2%})")
        
        if 'class_distribution' in checks:
            dist = checks['class_distribution']
            logger.info(f"     Class Distribution:")
            for cls, pct in dist.items():
                logger.info(f"       - Class {cls}: {pct:.2%}")
        
        if 'class_imbalance_ratio' in checks:
            ratio = checks['class_imbalance_ratio']
            logger.info(f"     Class Imbalance Ratio (Fraud/Legit): {ratio:.4f}")

# Main execution
if __name__ == "__main__":
    pipeline = DataIngestionPipeline()
    df = pipeline.run()

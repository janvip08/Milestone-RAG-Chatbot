import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("LocalScheduler")

def main():
    logger.info("==========================================")
    logger.info("    RUNNING SCHEDULER SIMULATION LOCALLY   ")
    logger.info("==========================================")
    
    # 1. Run Phase 1 Ingestion Pipeline
    logger.info("--- Step 1: Starting Phase 1 Ingestion ---")
    try:
        from ingestion.main import main as run_ingestion
        run_ingestion()
        logger.info("Phase 1 Ingestion Pipeline execution finished.")
    except Exception as e:
        logger.error(f"Error during Phase 1 Ingestion: {str(e)}", exc_info=True)
        sys.exit(1)
        
    # 2. Run Phase 2 Vector DB Seeding
    logger.info("--- Step 2: Starting Phase 2 Vector DB Seeding ---")
    try:
        from vector_db.src.main import seed_database
        success = seed_database()
        if success:
            logger.info("Phase 2 Vector DB Seeding execution finished successfully.")
        else:
            logger.error("Phase 2 Vector DB Seeding execution reported failure.")
            sys.exit(1)
    except Exception as e:
        logger.error(f"Error during Phase 2 Seeding: {str(e)}", exc_info=True)
        sys.exit(1)
        
    logger.info("==========================================")
    logger.info("   LOCAL SCHEDULER RUN COMPLETED SUCCESSFULLY!   ")
    logger.info("==========================================")

if __name__ == "__main__":
    main()

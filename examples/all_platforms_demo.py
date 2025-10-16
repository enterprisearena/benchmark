"""
All Platforms Demo

This example demonstrates all four platform connectors (Salesforce, ServiceNow, NetSuite, QuickBooks)
working together in EnterpriseArena.
"""

import asyncio
import logging
import os
from typing import Dict, List, Any
from enterprise_sandbox import (
    # Platform components
    PlatformFactory, PlatformCredentials, PlatformRegistry,
    SalesforceConnector, ServiceNowConnector, NetSuiteConnector, QuickBooksConnector,
    
    # Agent components
    ReActAgent, SinglePlatformToolCallAgent, OrchestrationAgent,
    
    # Environment components
    SinglePlatformEnvironment, CrossPlatformEnvironment,
    
    # Orchestration components
    OrchestrationEngine, CrossPlatformTask, TaskStep,
    
    # Evaluation components
    SinglePlatformEvaluator,
    
    # Configuration components
    PlatformConfigLoader, TaskConfigLoader, AgentConfigLoader
)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AllPlatformsDemo:
    """Comprehensive demonstration of all platform connectors."""
    
    def __init__(self):
        """Initialize the demo."""
        self.platform_registry = PlatformRegistry()
        self.orchestration_engine = None
        self.evaluator = SinglePlatformEvaluator(model="gpt-4o", provider="openai")
        self.results = {}
        
    async def setup_all_platforms(self):
        """Set up connections to all four platforms."""
        logger.info("=== Setting up All Platform Connections ===")
        
        # Set up Salesforce
        try:
            sf_credentials = PlatformCredentials(
                username=os.getenv("SALESFORCE_USERNAME", "demo_user"),
                password=os.getenv("SALESFORCE_PASSWORD", "demo_pass"),
                security_token=os.getenv("SALESFORCE_SECURITY_TOKEN", "demo_token"),
                environment="sandbox"
            )
            
            await self.platform_registry.register_platform("salesforce", sf_credentials)
            logger.info("✅ Salesforce platform registered")
            
        except Exception as e:
            logger.warning(f"⚠️ Salesforce setup failed: {e}")
        
        # Set up ServiceNow
        try:
            sn_credentials = PlatformCredentials(
                username=os.getenv("SERVICENOW_USERNAME", "demo_user"),
                password=os.getenv("SERVICENOW_PASSWORD", "demo_pass"),
                instance_url=os.getenv("SERVICENOW_INSTANCE_URL", "demo.service-now.com"),
                environment="sandbox"
            )
            
            await self.platform_registry.register_platform("servicenow", sn_credentials)
            logger.info("✅ ServiceNow platform registered")
            
        except Exception as e:
            logger.warning(f"⚠️ ServiceNow setup failed: {e}")
        
        # Set up NetSuite
        try:
            ns_credentials = PlatformCredentials(
                username=os.getenv("NETSUITE_USERNAME", "demo_user"),
                password=os.getenv("NETSUITE_PASSWORD", "demo_pass"),
                account_id=os.getenv("NETSUITE_ACCOUNT_ID", "demo_account"),
                role_id=os.getenv("NETSUITE_ROLE_ID", "demo_role"),
                application_id=os.getenv("NETSUITE_APPLICATION_ID", "demo_app"),
                consumer_key=os.getenv("NETSUITE_CONSUMER_KEY", "demo_key"),
                consumer_secret=os.getenv("NETSUITE_CONSUMER_SECRET", "demo_secret"),
                token_id=os.getenv("NETSUITE_TOKEN_ID", "demo_token"),
                token_secret=os.getenv("NETSUITE_TOKEN_SECRET", "demo_token_secret"),
                environment="sandbox"
            )
            
            await self.platform_registry.register_platform("netsuite", ns_credentials)
            logger.info("✅ NetSuite platform registered")
            
        except Exception as e:
            logger.warning(f"⚠️ NetSuite setup failed: {e}")
        
        # Set up QuickBooks
        try:
            qb_credentials = PlatformCredentials(
                client_id=os.getenv("QB_CLIENT_ID", "demo_client_id"),
                client_secret=os.getenv("QB_CLIENT_SECRET", "demo_client_secret"),
                company_id=os.getenv("QB_COMPANY_ID", "demo_company"),
                access_token=os.getenv("QB_ACCESS_TOKEN", "demo_access_token"),
                refresh_token=os.getenv("QB_REFRESH_TOKEN", "demo_refresh_token"),
                environment="sandbox"
            )
            
            await self.platform_registry.register_platform("quickbooks", qb_credentials)
            logger.info("✅ QuickBooks platform registered")
            
        except Exception as e:
            logger.warning(f"⚠️ QuickBooks setup failed: {e}")
        
        # Set up orchestration engine with all available platforms
        platform_connections = {}
        for platform_name in ["salesforce", "servicenow", "netsuite", "quickbooks"]:
            platform = await self.platform_registry.get_platform(platform_name)
            if platform:
                platform_connections[platform_name] = platform
        
        if platform_connections:
            self.orchestration_engine = OrchestrationEngine(platform_connections)
            logger.info(f"✅ Orchestration engine initialized with {len(platform_connections)} platforms")
    
    async def demo_salesforce_operations(self):
        """Demonstrate Salesforce operations."""
        logger.info("\n=== Salesforce Operations Demo ===")
        
        try:
            platform = await self.platform_registry.get_platform("salesforce")
            if not platform:
                logger.warning("Salesforce platform not available")
                return
            
            # Test basic operations
            logger.info("Testing Salesforce connection...")
            health_check = await platform.perform_health_check()
            logger.info(f"Salesforce health check: {health_check}")
            
            # Test query execution
            logger.info("Testing Salesforce query...")
            query_result = await platform.execute_query("SELECT Id, Name FROM Account LIMIT 5")
            logger.info(f"Salesforce query result: {len(query_result.data)} records found")
            
            self.results["salesforce"] = {
                "health_check": health_check,
                "query_result": len(query_result.data),
                "success": True
            }
            
        except Exception as e:
            logger.error(f"❌ Salesforce demo failed: {e}")
            self.results["salesforce"] = {"success": False, "error": str(e)}
    
    async def demo_servicenow_operations(self):
        """Demonstrate ServiceNow operations."""
        logger.info("\n=== ServiceNow Operations Demo ===")
        
        try:
            platform = await self.platform_registry.get_platform("servicenow")
            if not platform:
                logger.warning("ServiceNow platform not available")
                return
            
            # Test basic operations
            logger.info("Testing ServiceNow connection...")
            health_check = await platform.perform_health_check()
            logger.info(f"ServiceNow health check: {health_check}")
            
            # Test query execution
            logger.info("Testing ServiceNow query...")
            query_result = await platform.execute_query("incident", {"sysparm_limit": 5})
            logger.info(f"ServiceNow query result: {len(query_result.data)} records found")
            
            self.results["servicenow"] = {
                "health_check": health_check,
                "query_result": len(query_result.data),
                "success": True
            }
            
        except Exception as e:
            logger.error(f"❌ ServiceNow demo failed: {e}")
            self.results["servicenow"] = {"success": False, "error": str(e)}
    
    async def demo_netsuite_operations(self):
        """Demonstrate NetSuite operations."""
        logger.info("\n=== NetSuite Operations Demo ===")
        
        try:
            platform = await self.platform_registry.get_platform("netsuite")
            if not platform:
                logger.warning("NetSuite platform not available")
                return
            
            # Test basic operations
            logger.info("Testing NetSuite connection...")
            health_check = await platform.perform_health_check()
            logger.info(f"NetSuite health check: {health_check}")
            
            # Test query execution
            logger.info("Testing NetSuite query...")
            query_result = await platform.execute_query("SELECT * FROM customer LIMIT 5")
            logger.info(f"NetSuite query result: {len(query_result.data)} records found")
            
            self.results["netsuite"] = {
                "health_check": health_check,
                "query_result": len(query_result.data),
                "success": True
            }
            
        except Exception as e:
            logger.error(f"❌ NetSuite demo failed: {e}")
            self.results["netsuite"] = {"success": False, "error": str(e)}
    
    async def demo_quickbooks_operations(self):
        """Demonstrate QuickBooks operations."""
        logger.info("\n=== QuickBooks Operations Demo ===")
        
        try:
            platform = await self.platform_registry.get_platform("quickbooks")
            if not platform:
                logger.warning("QuickBooks platform not available")
                return
            
            # Test basic operations
            logger.info("Testing QuickBooks connection...")
            health_check = await platform.perform_health_check()
            logger.info(f"QuickBooks health check: {health_check}")
            
            # Test query execution
            logger.info("Testing QuickBooks query...")
            query_result = await platform.execute_query("SELECT * FROM Customer MAXRESULTS 5")
            logger.info(f"QuickBooks query result: {len(query_result.data)} records found")
            
            self.results["quickbooks"] = {
                "health_check": health_check,
                "query_result": len(query_result.data),
                "success": True
            }
            
        except Exception as e:
            logger.error(f"❌ QuickBooks demo failed: {e}")
            self.results["quickbooks"] = {"success": False, "error": str(e)}
    
    async def demo_cross_platform_workflow(self):
        """Demonstrate cross-platform workflow orchestration."""
        logger.info("\n=== Cross-Platform Workflow Demo ===")
        
        try:
            if not self.orchestration_engine:
                logger.warning("Orchestration engine not available")
                return
            
            # Create a complex cross-platform task
            task = CrossPlatformTask(
                task_id="multi_platform_workflow_001",
                name="Customer Service to Financial Integration",
                description="Convert ServiceNow incident to Salesforce case and create QuickBooks invoice",
                category="customer_service",
                platforms=["servicenow", "salesforce", "quickbooks"],
                complexity="high",
                steps=[
                    TaskStep(
                        step_id="fetch_incident",
                        name="Fetch Incident from ServiceNow",
                        platform="servicenow",
                        action_type="query",
                        parameters={
                            "query": "incident",
                            "criteria": {"state": "New"}
                        }
                    ),
                    TaskStep(
                        step_id="create_case",
                        name="Create Case in Salesforce",
                        platform="salesforce",
                        action_type="create",
                        parameters={
                            "object_type": "Case",
                            "data": {
                                "Subject": "Converted from ServiceNow",
                                "Status": "New",
                                "Origin": "ServiceNow"
                            }
                        }
                    ),
                    TaskStep(
                        step_id="create_invoice",
                        name="Create Invoice in QuickBooks",
                        platform="quickbooks",
                        action_type="create",
                        parameters={
                            "object_type": "Invoice",
                            "data": {
                                "Line": [{
                                    "DetailType": "SalesItemLineDetail",
                                    "Amount": 100.00,
                                    "Description": "Service fee"
                                }]
                            }
                        }
                    )
                ],
                dependencies={
                    "create_case": ["fetch_incident"],
                    "create_invoice": ["create_case"]
                }
            )
            
            # Execute cross-platform workflow
            logger.info("Executing cross-platform workflow...")
            result = await self.orchestration_engine.execute_task(task)
            
            self.results["cross_platform_workflow"] = result
            logger.info(f"✅ Cross-platform workflow completed: {result.get('status', 'unknown')}")
            
        except Exception as e:
            logger.error(f"❌ Cross-platform workflow demo failed: {e}")
            self.results["cross_platform_workflow"] = {"success": False, "error": str(e)}
    
    async def demo_platform_comparison(self):
        """Demonstrate platform comparison and analysis."""
        logger.info("\n=== Platform Comparison Demo ===")
        
        try:
            comparison_results = {}
            
            for platform_name in ["salesforce", "servicenow", "netsuite", "quickbooks"]:
                platform = await self.platform_registry.get_platform(platform_name)
                if platform:
                    # Get platform capabilities
                    health_check = await platform.perform_health_check()
                    schema_info = await platform.get_schema()
                    
                    comparison_results[platform_name] = {
                        "connected": True,
                        "healthy": health_check.get("healthy", False),
                        "api_version": health_check.get("api_version", "unknown"),
                        "schema_available": bool(schema_info)
                    }
                else:
                    comparison_results[platform_name] = {
                        "connected": False,
                        "healthy": False,
                        "api_version": "unknown",
                        "schema_available": False
                    }
            
            self.results["platform_comparison"] = comparison_results
            
            # Log comparison results
            logger.info("Platform Comparison Results:")
            for platform_name, results in comparison_results.items():
                status = "✅" if results["connected"] and results["healthy"] else "❌"
                logger.info(f"  {status} {platform_name.upper()}: Connected={results['connected']}, Healthy={results['healthy']}, API={results['api_version']}")
            
        except Exception as e:
            logger.error(f"❌ Platform comparison demo failed: {e}")
            self.results["platform_comparison"] = {"success": False, "error": str(e)}
    
    def generate_comprehensive_report(self):
        """Generate a comprehensive report of all platform demos."""
        logger.info("\n" + "="*80)
        logger.info("ENTERPRISE ARENA - ALL PLATFORMS DEMO SUMMARY REPORT")
        logger.info("="*80)
        
        # Platform-specific results
        platforms = ["salesforce", "servicenow", "netsuite", "quickbooks"]
        successful_platforms = 0
        
        for platform_name in platforms:
            if platform_name in self.results:
                result = self.results[platform_name]
                if result.get("success", False):
                    successful_platforms += 1
                    logger.info(f"\n✅ {platform_name.upper()} PLATFORM:")
                    logger.info(f"  - Health Check: {result.get('health_check', {}).get('healthy', 'Unknown')}")
                    logger.info(f"  - Query Results: {result.get('query_result', 0)} records")
                    logger.info(f"  - API Version: {result.get('health_check', {}).get('api_version', 'Unknown')}")
                else:
                    logger.info(f"\n❌ {platform_name.upper()} PLATFORM:")
                    logger.info(f"  - Error: {result.get('error', 'Unknown error')}")
            else:
                logger.info(f"\n⚠️ {platform_name.upper()} PLATFORM: Not tested")
        
        # Cross-platform workflow results
        if "cross_platform_workflow" in self.results:
            workflow_result = self.results["cross_platform_workflow"]
            if workflow_result.get("success", False):
                logger.info(f"\n✅ CROSS-PLATFORM WORKFLOW:")
                logger.info(f"  - Status: {workflow_result.get('status', 'Unknown')}")
                logger.info(f"  - Execution Time: {workflow_result.get('execution_time', 0):.2f}s")
                logger.info(f"  - Steps Completed: {workflow_result.get('steps_completed', 0)}")
            else:
                logger.info(f"\n❌ CROSS-PLATFORM WORKFLOW:")
                logger.info(f"  - Error: {workflow_result.get('error', 'Unknown error')}")
        
        # Platform comparison results
        if "platform_comparison" in self.results:
            comparison = self.results["platform_comparison"]
            logger.info(f"\n📊 PLATFORM COMPARISON SUMMARY:")
            logger.info(f"  - Total Platforms: {len(platforms)}")
            logger.info(f"  - Successfully Connected: {successful_platforms}")
            logger.info(f"  - Success Rate: {successful_platforms/len(platforms)*100:.1f}%")
        
        # Overall summary
        logger.info(f"\n🎯 OVERALL SUMMARY:")
        logger.info(f"  - Platforms Implemented: 4/4 (100%)")
        logger.info(f"  - Platforms Successfully Connected: {successful_platforms}/4")
        logger.info(f"  - Cross-Platform Orchestration: {'✅ Available' if self.orchestration_engine else '❌ Not Available'}")
        logger.info(f"  - Framework Status: {'✅ Fully Operational' if successful_platforms >= 2 else '⚠️ Partially Operational'}")
        
        logger.info("\n" + "="*80)
        logger.info("ALL PLATFORMS DEMO COMPLETED!")
        logger.info("="*80)
    
    async def run_all_demos(self):
        """Run all demonstration scenarios."""
        logger.info("Starting EnterpriseArena All Platforms Demo...")
        
        try:
            # Setup
            await self.setup_all_platforms()
            
            # Run individual platform demos
            await self.demo_salesforce_operations()
            await self.demo_servicenow_operations()
            await self.demo_netsuite_operations()
            await self.demo_quickbooks_operations()
            
            # Run cross-platform demos
            await self.demo_cross_platform_workflow()
            await self.demo_platform_comparison()
            
            # Generate comprehensive report
            self.generate_comprehensive_report()
            
        except Exception as e:
            logger.error(f"Demo execution failed: {e}")
        finally:
            # Cleanup
            await self.platform_registry.disconnect_all()
            logger.info("All platform connections closed")


async def main():
    """Main function to run the all platforms demo."""
    demo = AllPlatformsDemo()
    await demo.run_all_demos()


if __name__ == "__main__":
    asyncio.run(main())

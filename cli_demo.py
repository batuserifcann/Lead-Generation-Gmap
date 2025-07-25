#!/usr/bin/env python3
"""
Command Line Demo for Business Lead Automation System
Test all functionality without GUI
"""
import sys
import os
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.excel_manager import ExcelManager
from core.website_detector import WebsiteDetector
from core.message_templates import MessageTemplateManager
from core.rate_limiter import RateLimiter
from utils.logger import get_logger, log_info

def print_header(title):
    """Print a formatted header"""
    print("\n" + "="*60)
    print(f"🚀 {title}")
    print("="*60)

def print_section(title):
    """Print a formatted section"""
    print(f"\n📋 {title}")
    print("-" * 40)

def demo_excel_manager():
    """Demo Excel Manager functionality"""
    print_section("EXCEL MANAGER DEMO")
    
    # Create sample data
    import pandas as pd
    sample_data = [
        {
            'business_name': 'Mehmet\'s Restaurant',
            'address': 'Konak, İzmir',
            'phone': '0232 123 45 67',
            'email': 'info@mehmets.com',
            'website': 'https://mehmets.com',
            'industry': 'Restaurant',
            'location': 'İzmir',
            'contact_status': 'Not Contacted',
            'has_website': True
        },
        {
            'business_name': 'Ankara Construction Co.',
            'address': 'Çankaya, Ankara',
            'phone': '0312 987 65 43',
            'email': '',
            'website': '',
            'industry': 'Construction',
            'location': 'Ankara',
            'contact_status': 'Not Contacted',
            'has_website': False
        },
        {
            'business_name': 'İstanbul Tech Solutions',
            'address': 'Beşiktaş, İstanbul',
            'phone': '0212 555 12 34',
            'email': 'contact@istanbultech.com',
            'website': 'https://istanbultech.com',
            'industry': 'Technology',
            'location': 'İstanbul',
            'contact_status': 'Contacted',
            'has_website': True
        }
    ]
    
    # Initialize Excel Manager
    excel_manager = ExcelManager('demo_data.xlsx')
    excel_manager.data = pd.DataFrame(sample_data)
    excel_manager.save_data()
    
    print(f"✅ Created demo data with {len(sample_data)} businesses")
    
    # Show statistics
    stats = excel_manager.get_statistics()
    print(f"📊 Statistics:")
    print(f"   Total businesses: {stats['total_businesses']}")
    print(f"   Contacted: {stats['contacted']}")
    print(f"   Not contacted: {stats['not_contacted']}")
    print(f"   With websites: {stats['with_websites']}")
    print(f"   Without websites: {stats['without_websites']}")
    
    # Test search
    search_results = excel_manager.search_businesses('Restaurant')
    print(f"🔍 Search for 'Restaurant': {len(search_results)} results")
    
    return excel_manager

def demo_website_detector():
    """Demo Website Detector functionality"""
    print_section("WEBSITE DETECTOR DEMO")
    
    detector = WebsiteDetector(timeout=10)
    
    # Test URLs
    test_urls = [
        'https://google.com',
        'https://github.com',
        'nonexistent-website-12345.com',
        ''
    ]
    
    print("🌐 Testing website detection:")
    for url in test_urls:
        result = detector.check_website_exists(url)
        status_icon = "✅" if result['exists'] else "❌"
        print(f"   {status_icon} {url or '(empty)'}: {result['status']}")
    
    return detector

def demo_message_templates():
    """Demo Message Templates functionality"""
    print_section("MESSAGE TEMPLATES DEMO")
    
    template_manager = MessageTemplateManager()
    
    # Show available templates
    templates = template_manager.get_all_templates()
    print(f"📝 Available templates ({len(templates)}):")
    for template_id, template in templates.items():
        print(f"   • {template['name']} ({template_id})")
    
    # Demo personalization
    business_data = {
        'business_name': 'Mehmet\'s Restaurant',
        'location': 'İzmir',
        'industry': 'Restaurant'
    }
    
    personalized = template_manager.personalize_message('restaurant_website', business_data)
    print(f"\n✉️ Personalized message sample:")
    print("-" * 40)
    print(personalized[:300] + "..." if len(personalized) > 300 else personalized)
    print("-" * 40)
    
    return template_manager

def demo_rate_limiter():
    """Demo Rate Limiter functionality"""
    print_section("RATE LIMITER DEMO")
    
    rate_limiter = RateLimiter(max_per_hour=10, delay_between=5)
    
    print("⏱️ Rate limiter configuration:")
    stats = rate_limiter.get_statistics()
    print(f"   Max per hour: {stats['max_per_hour']}")
    print(f"   Delay between messages: {stats['delay_between_messages']}s")
    print(f"   Can send now: {stats['can_send_now']}")
    
    # Simulate sending messages
    print(f"\n📤 Simulating message sending:")
    for i in range(3):
        if rate_limiter.can_send_message():
            rate_limiter.record_message_sent()
            print(f"   ✅ Message {i+1} sent")
            print(f"   ⏳ Next available in: {rate_limiter.get_time_until_next_slot()}")
        else:
            wait_time = rate_limiter.get_next_available_time()
            print(f"   ⏸️ Rate limited - wait {wait_time}s")
    
    return rate_limiter

def demo_integration():
    """Demo integration between components"""
    print_section("INTEGRATION DEMO")

    # Load the demo data
    excel_manager = ExcelManager('demo_data.xlsx')

    if excel_manager.data.empty:
        print("📊 Creating demo data for integration test...")
        # Create the demo data if it doesn't exist
        demo_excel_manager()
        excel_manager = ExcelManager('demo_data.xlsx')
    
    # Get businesses without websites
    businesses_without_websites = excel_manager.get_businesses_without_websites()
    print(f"🎯 Businesses without websites: {len(businesses_without_websites)}")
    
    # Show targeting opportunities
    template_manager = MessageTemplateManager()
    
    print(f"\n📊 Targeting Analysis:")
    for _, business in businesses_without_websites.iterrows():
        print(f"   • {business['business_name']} ({business['industry']}) - {business['location']}")
        
        # Show personalized message preview
        if business['industry'].lower() == 'construction':
            template_id = 'construction_website'
        elif business['industry'].lower() == 'restaurant':
            template_id = 'restaurant_website'
        else:
            template_id = 'general_business'
        
        personalized = template_manager.personalize_message(template_id, business.to_dict())
        if personalized:
            preview = personalized.split('\n')[0]  # First line only
            print(f"     📝 Message preview: {preview}")

def interactive_menu():
    """Interactive menu for testing"""
    while True:
        print_header("BUSINESS LEAD AUTOMATION - CLI DEMO")
        print("Choose a demo to run:")
        print("1. 📊 Excel Manager Demo")
        print("2. 🌐 Website Detector Demo")
        print("3. 📝 Message Templates Demo")
        print("4. ⏱️ Rate Limiter Demo")
        print("5. 🔗 Integration Demo")
        print("6. 🏃 Run All Demos")
        print("0. ❌ Exit")
        
        choice = input("\nEnter your choice (0-6): ").strip()
        
        try:
            if choice == '1':
                demo_excel_manager()
            elif choice == '2':
                demo_website_detector()
            elif choice == '3':
                demo_message_templates()
            elif choice == '4':
                demo_rate_limiter()
            elif choice == '5':
                demo_integration()
            elif choice == '6':
                demo_excel_manager()
                demo_website_detector()
                demo_message_templates()
                demo_rate_limiter()
                demo_integration()
            elif choice == '0':
                print("\n👋 Goodbye!")
                break
            else:
                print("❌ Invalid choice. Please try again.")
                
        except KeyboardInterrupt:
            print("\n\n⏹️ Demo interrupted by user")
            break
        except Exception as e:
            print(f"\n❌ Error during demo: {e}")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    print_header("BUSINESS LEAD AUTOMATION SYSTEM - CLI DEMO")
    print("🎯 This demo shows all system functionality without GUI")
    print("📝 Perfect for testing in headless environments")
    
    try:
        interactive_menu()
    except KeyboardInterrupt:
        print("\n\n👋 Demo terminated by user")
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)

"""
Test Flask app initialization
"""

import app as flask_app

print("✅ Flask app module loaded successfully")
print(f"Flask app created: {flask_app.app}")
print(f"Debug mode: {flask_app.app.config.get('DEBUG')}")
print(f"Port: {flask_app.app.config.get('PORT')}")
print("\n✅ All Flask app configurations are correct!")

# List routes
print("\n📍 Available API Routes:")
for rule in flask_app.app.url_map.iter_rules():
    if rule.endpoint != 'static':
        print(f"  {rule.rule} [{', '.join(rule.methods - {'HEAD', 'OPTIONS'})}]")

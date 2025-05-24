from context_api_fetcher import get_client_context

def test_client_context():
    client_name = "UIPath"
    context = get_client_context(client_name)

    if context:
        print("✅ Context obținut cu succes:")
        print("="*40)
        print(context)
    else:
        print("❌ Nu s-a putut obține context pentru", client_name)

if __name__ == "__main__":
    test_client_context()

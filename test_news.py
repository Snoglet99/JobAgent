from fetch_news import fetch_company_news_summary

test = fetch_company_news_summary(
    company_name="Commonwealth Bank",
    objectives=["expanding market share", "client relationship"]
)

print("=== NEWS SUMMARY ===")
print(test["news_summary"])
print("=== SOURCES ===")
for s in test["sources"]:
    print("-", s)

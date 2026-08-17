"""
The 100 apps from the assignment brief, with category + hint URL.
This is the ONLY hand-entered file. Everything downstream is agent-generated.
"""

APPS = [
    # 1. CRM and Sales
    ("Salesforce", "CRM and Sales", "salesforce.com"),
    ("HubSpot", "CRM and Sales", "hubspot.com"),
    ("Pipedrive", "CRM and Sales", "pipedrive.com"),
    ("Attio", "CRM and Sales", "attio.com"),
    ("Twenty", "CRM and Sales", "twenty.com"),
    ("Podio", "CRM and Sales", "podio.com"),
    ("Zoho CRM", "CRM and Sales", "zoho.com/crm"),
    ("Close", "CRM and Sales", "close.com"),
    ("Copper", "CRM and Sales", "copper.com"),
    ("DealCloud", "CRM and Sales", "api.docs.dealcloud.com"),

    # 2. Support and Helpdesk
    ("Zendesk", "Support and Helpdesk", "zendesk.com"),
    ("Intercom", "Support and Helpdesk", "intercom.com"),
    ("Freshdesk", "Support and Helpdesk", "freshdesk.com"),
    ("Front", "Support and Helpdesk", "front.com"),
    ("Pylon", "Support and Helpdesk", "usepylon.com"),
    ("LiveAgent", "Support and Helpdesk", "liveagent.com"),
    ("Plain", "Support and Helpdesk", "plain.com"),
    ("Help Scout", "Support and Helpdesk", "helpscout.com"),
    ("Gorgias", "Support and Helpdesk", "gorgias.com"),
    ("Gladly", "Support and Helpdesk", "gladly.com"),

    # 3. Communications and Messaging
    ("Slack", "Communications and Messaging", "slack.com"),
    ("Twilio", "Communications and Messaging", "twilio.com"),
    ("Zoho Cliq", "Communications and Messaging", "zoho.com/cliq"),
    ("Lark (Larksuite)", "Communications and Messaging", "open.larksuite.com"),
    ("Pumble", "Communications and Messaging", "pumble.com"),
    ("Discord", "Communications and Messaging", "discord.com"),
    ("Telegram", "Communications and Messaging", "core.telegram.org"),
    ("WhatsApp Business", "Communications and Messaging", "developers.facebook.com/docs/whatsapp"),
    ("Aircall", "Communications and Messaging", "aircall.io"),
    ("Vonage", "Communications and Messaging", "developer.vonage.com"),

    # 4. Marketing, Ads, Email and Social
    ("Google Ads", "Marketing Ads Email Social", "developers.google.com/google-ads"),
    ("Meta Ads", "Marketing Ads Email Social", "developers.facebook.com/docs/marketing-apis"),
    ("LinkedIn Ads", "Marketing Ads Email Social", "learn.microsoft.com/linkedin/marketing"),
    ("GoHighLevel", "Marketing Ads Email Social", "highlevel.stoplight.io"),
    ("Mailchimp", "Marketing Ads Email Social", "mailchimp.com/developer"),
    ("Klaviyo", "Marketing Ads Email Social", "developers.klaviyo.com"),
    ("systeme.io", "Marketing Ads Email Social", "systeme.io"),
    ("Pinterest", "Marketing Ads Email Social", "developers.pinterest.com"),
    ("Threads (Meta)", "Marketing Ads Email Social", "developers.facebook.com/docs/threads"),
    ("SendGrid", "Marketing Ads Email Social", "sendgrid.com"),

    # 5. Ecommerce
    ("Shopify", "Ecommerce", "shopify.dev"),
    ("WooCommerce", "Ecommerce", "woocommerce.com/document/woocommerce-rest-api"),
    ("BigCommerce", "Ecommerce", "developer.bigcommerce.com"),
    ("Salesforce Commerce Cloud", "Ecommerce", "developer.salesforce.com/docs/commerce"),
    ("Magento (Adobe Commerce)", "Ecommerce", "developer.adobe.com/commerce"),
    ("Squarespace", "Ecommerce", "developers.squarespace.com"),
    ("Ecwid", "Ecommerce", "api-docs.ecwid.com"),
    ("Gumroad", "Ecommerce", "gumroad.com/api"),
    ("Amazon Selling Partner", "Ecommerce", "developer-docs.amazon.com/sp-api"),
    ("fanbasis", "Ecommerce", "fanbasis.com"),

    # 6. Data, SEO and Scraping
    ("DataForSEO", "Data SEO Scraping", "docs.dataforseo.com"),
    ("SE Ranking", "Data SEO Scraping", "seranking.com/api"),
    ("Ahrefs", "Data SEO Scraping", "ahrefs.com/api"),
    ("MrScraper", "Data SEO Scraping", "docs.mrscraper.com"),
    ("Apify", "Data SEO Scraping", "docs.apify.com"),
    ("Firecrawl", "Data SEO Scraping", "firecrawl.dev"),
    ("Bright Data", "Data SEO Scraping", "brightdata.com"),
    ("Sherlock", "Data SEO Scraping", "github.com/sherlock-project/sherlock"),
    ("Waterfall.io", "Data SEO Scraping", "waterfall.io"),
    ("Clay", "Data SEO Scraping", "clay.com"),

    # 7. Developer, Infra and Data platforms
    ("GitHub", "Developer Infra Data", "docs.github.com/rest"),
    ("Vercel", "Developer Infra Data", "vercel.com/docs/rest-api"),
    ("Netlify", "Developer Infra Data", "docs.netlify.com/api"),
    ("Cloudflare", "Developer Infra Data", "developers.cloudflare.com/api"),
    ("Supabase", "Developer Infra Data", "supabase.com/docs"),
    ("Neo4j", "Developer Infra Data", "neo4j.com/docs/api"),
    ("Snowflake", "Developer Infra Data", "docs.snowflake.com"),
    ("MongoDB Atlas", "Developer Infra Data", "mongodb.com/docs/atlas/api"),
    ("Datadog", "Developer Infra Data", "docs.datadoghq.com/api"),
    ("Sentry", "Developer Infra Data", "docs.sentry.io/api"),

    # 8. Productivity and Project Management
    ("Notion", "Productivity and PM", "developers.notion.com"),
    ("Airtable", "Productivity and PM", "airtable.com/developers"),
    ("Linear", "Productivity and PM", "developers.linear.app"),
    ("Jira", "Productivity and PM", "developer.atlassian.com"),
    ("Asana", "Productivity and PM", "developers.asana.com"),
    ("Monday.com", "Productivity and PM", "developer.monday.com"),
    ("ClickUp", "Productivity and PM", "clickup.com/api"),
    ("Coda", "Productivity and PM", "coda.io/developers"),
    ("Smartsheet", "Productivity and PM", "smartsheet.com/developers"),
    ("Harvest", "Productivity and PM", "help.getharvest.com/api-v2"),

    # 9. Finance and Fintech
    ("Stripe", "Finance and Fintech", "stripe.com/docs/api"),
    ("Plaid", "Finance and Fintech", "plaid.com/docs"),
    ("Binance", "Finance and Fintech", "binance-docs.github.io"),
    ("Paygent Connect", "Finance and Fintech", "paygent"),
    ("iPayX", "Finance and Fintech", "ipayx.ai/docs"),
    ("QuickBooks", "Finance and Fintech", "developer.intuit.com"),
    ("Xero", "Finance and Fintech", "developer.xero.com"),
    ("Brex", "Finance and Fintech", "developer.brex.com"),
    ("Ramp", "Finance and Fintech", "docs.ramp.com"),
    ("PitchBook", "Finance and Fintech", "pitchbook.com"),

    # 10. AI, Research and Media-native
    ("NotebookLM", "AI Research Media", "cloud.google.com/gemini"),
    ("Otter AI", "AI Research Media", "help.otter.ai"),
    ("Fathom", "AI Research Media", "fathom.video"),
    ("Consensus", "AI Research Media", "consensus.app"),
    ("Reducto", "AI Research Media", "reducto.ai"),
    ("Devin", "AI Research Media", "docs.devin.ai"),
    ("higgsfield", "AI Research Media", "higgsfield.ai/cli"),
    ("Mermaid CLI", "AI Research Media", "github.com/mermaid-js/mermaid-cli"),
    ("YouTube Transcript", "AI Research Media", "transcriptapi.com"),
    ("Grain", "AI Research Media", "grain.com"),
]

assert len(APPS) == 100, f"Expected 100 apps, got {len(APPS)}"

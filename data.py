from langchain_core.documents import Document
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_community.vectorstores import FAISS


raw_docs = [
    {"title": "Tomato Planting Guide", "content": "Tomatoes grow best in warm weather with full sunlight. Use loamy soil with a pH of 6.0 to 6.8. Fertilize with 10-10-10 fertilizer every 2 weeks."},
    {"title": "Spinach Growing Tips", "content": "Spinach prefers cool climates and can be sown in early spring or fall. Water regularly and harvest when leaves are 4-6 inches long."},
    {"title": "Neem Oil Uses", "content": "Neem oil is an organic pesticide useful for aphids, whiteflies, and spider mites. Mix 2 tablespoons with 1 liter of water and spray weekly."},
    {"title": "Aloe Vera Care", "content": "Aloe vera needs bright indirect sunlight and sandy soil. Water deeply but infrequently—every 2-3 weeks depending on climate."},
    {"title": "Composting Basics", "content": "Compost is made from green materials like vegetable scraps and brown materials like dried leaves. Turn the pile weekly to speed up decomposition."},
    {"title": "Watering Schedule for Lawns", "content": "Lawns typically need 1 inch of water per week. Water early in the morning to minimize evaporation and fungal diseases."},
    {"title": "Pruning Roses", "content": "Prune rose bushes in early spring before new growth starts. Remove dead or weak stems and cut just above outward-facing buds."},
    {"title": "Indoor Herb Gardening", "content": "Herbs like basil, parsley, and mint grow well indoors near a sunny window. Use well-draining pots and avoid overwatering."},
    {"title": "Pest Control for Vegetables", "content": "Use companion planting, neem oil, and row covers to control pests naturally. Regular inspection helps catch infestations early."},
    {"title": "Mulching Benefits", "content": "Mulch retains soil moisture, suppresses weeds, and regulates soil temperature. Organic mulches like straw or wood chips break down over time, enriching the soil."},
    {"title": "Caring for Succulents", "content": "Succulents need at least 6 hours of bright, indirect sunlight daily. Use cactus mix soil and water only when the soil is completely dry."},
    {"title": "Container Gardening Tips", "content": "Use pots with drainage holes and choose compact plant varieties. Water more frequently than ground-planted gardens and fertilize every 4-6 weeks."},
    {"title": "When to Plant Carrots", "content": "Carrots grow best in loose, sandy soil and cooler weather. Plant seeds 2-3 weeks before the last spring frost and thin seedlings to 2 inches apart."},
    {"title": "Dealing with Powdery Mildew", "content": "Powdery mildew appears as white powder on leaves. Remove affected leaves and spray with a solution of 1 tablespoon baking soda, ½ teaspoon liquid soap, and 1 liter water."},
    {"title": "Transplanting Seedlings", "content": "Harden off seedlings by exposing them to outdoor conditions gradually over a week. Transplant on a cloudy day or in the evening to reduce shock."},
    {"title": "Best Plants for Shade", "content": "Ferns, hostas, impatiens, and begonias thrive in low-light conditions. Ensure well-draining soil and avoid overwatering."},
    {"title": "How to Start a Garden Bed", "content": "Clear the area of weeds, test the soil, and amend with compost. Raised beds are great for drainage and control over soil quality."},
    {"title": "Using Epsom Salt in the Garden", "content": "Epsom salt provides magnesium and sulfur. Mix 1 tablespoon per gallon of water and apply to tomatoes, peppers, or roses once a month."},
    {"title": "Harvesting Herbs Properly", "content": "Harvest herbs in the morning after dew has dried. Use clean scissors and snip just above a leaf node to encourage bushier growth."},
    {"title": "Winterizing Your Garden", "content": "Remove dead plants, add mulch for insulation, and cover tender perennials. Clean tools and store them dry to prevent rust."}

]

# Converting Into Document Objects
docs = [Document(page_content=doc["content"], metadata={"title": doc["title"]}) for doc in raw_docs]

embedding_model = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

# Creating FAISS Vector Store
vector_store = FAISS.from_documents(docs, embedding_model)
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import json
from dataclasses import dataclass
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sentence_transformers import SentenceTransformer
import hashlib

@dataclass
class PropertyData:
    """Structure for property comparable data"""
    # Core identifiers
    zpid: str
    address: str
    city: str
    state: str
    zip_code: str
    
    # Property characteristics
    price: float
    bedrooms: int
    bathrooms: float
    square_feet: int
    lot_size: Optional[float]
    year_built: int
    property_type: str  # Single Family, Condo, Townhouse, etc.
    
    # Sale information
    sale_date: datetime
    days_on_market: Optional[int]
    price_per_sqft: float
    
    # Location features
    latitude: float
    longitude: float
    neighborhood: Optional[str]
    school_district: Optional[str]
    
    # Additional features
    garage_spaces: Optional[int]
    stories: Optional[int]
    pool: bool
    fireplace: bool
    updated_kitchen: bool
    updated_bathrooms: bool
    
    # Market context
    market_trend: Optional[str]  # Hot, Normal, Cold
    listing_views: Optional[int]

class ZillowEmbeddingGenerator:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the embedding generator for Zillow comparables
        
        Args:
            model_name: Sentence transformer model for text embeddings
        """
        self.text_model = SentenceTransformer(model_name)
        self.scalers = {}
        self.encoders = {}
        self.feature_weights = {
            'numerical': 0.4,
            'categorical': 0.3,
            'location': 0.2,
            'text': 0.1
        }
        
    def _normalize_numerical_features(self, properties: List[PropertyData]) -> np.ndarray:
        """Extract and normalize numerical features"""
        numerical_features = []
        feature_names = [
            'price', 'bedrooms', 'bathrooms', 'square_feet', 'lot_size',
            'year_built', 'days_on_market', 'price_per_sqft', 'garage_spaces',
            'stories', 'listing_views'
        ]
        
        for prop in properties:
            features = []
            for feature in feature_names:
                value = getattr(prop, feature, None)
                if value is None:
                    # Handle missing values with median or appropriate default
                    if feature in ['lot_size', 'days_on_market', 'garage_spaces', 'stories', 'listing_views']:
                        value = 0
                    elif feature == 'year_built':
                        value = 1980  # Default year
                    else:
                        value = 0
                features.append(float(value))
            numerical_features.append(features)
        
        numerical_array = np.array(numerical_features)
        
        # Fit scaler if not already fitted
        if 'numerical' not in self.scalers:
            self.scalers['numerical'] = StandardScaler()
            self.scalers['numerical'].fit(numerical_array)
        
        return self.scalers['numerical'].transform(numerical_array)
    
    def _encode_categorical_features(self, properties: List[PropertyData]) -> np.ndarray:
        """Encode categorical features"""
        categorical_features = []
        feature_names = ['property_type', 'neighborhood', 'school_district', 'market_trend']
        
        # Prepare data for encoding
        cat_data = {}
        for feature in feature_names:
            cat_data[feature] = [getattr(prop, feature, 'Unknown') or 'Unknown' for prop in properties]
        
        encoded_features = []
        for feature in feature_names:
            if feature not in self.encoders:
                self.encoders[feature] = LabelEncoder()
                self.encoders[feature].fit(cat_data[feature])
            
            encoded = self.encoders[feature].transform(cat_data[feature])
            # One-hot encode to prevent ordinal relationships
            unique_vals = len(self.encoders[feature].classes_)
            one_hot = np.eye(unique_vals)[encoded]
            encoded_features.append(one_hot)
        
        return np.concatenate(encoded_features, axis=1)
    
    def _encode_binary_features(self, properties: List[PropertyData]) -> np.ndarray:
        """Encode binary features"""
        binary_features = []
        feature_names = ['pool', 'fireplace', 'updated_kitchen', 'updated_bathrooms']
        
        for prop in properties:
            features = []
            for feature in feature_names:
                value = getattr(prop, feature, False)
                features.append(1.0 if value else 0.0)
            binary_features.append(features)
        
        return np.array(binary_features)
    
    def _generate_location_embeddings(self, properties: List[PropertyData]) -> np.ndarray:
        """Generate location-based embeddings using coordinates and clustering"""
        coords = np.array([[prop.latitude, prop.longitude] for prop in properties])
        
        # Normalize coordinates
        if 'location' not in self.scalers:
            self.scalers['location'] = StandardScaler()
            self.scalers['location'].fit(coords)
        
        normalized_coords = self.scalers['location'].transform(coords)
        
        # Add distance from city center (assuming major metro areas)
        city_centers = {
            'seattle': (47.6062, -122.3321),
            'san francisco': (37.7749, -122.4194),
            'los angeles': (34.0522, -118.2437),
            'new york': (40.7128, -74.0060),
            'chicago': (41.8781, -87.6298)
        }
        
        distance_features = []
        for prop in properties:
            city_distances = []
            for center_coords in city_centers.values():
                dist = np.sqrt((prop.latitude - center_coords[0])**2 + 
                             (prop.longitude - center_coords[1])**2)
                city_distances.append(dist)
            distance_features.append(city_distances)
        
        distance_array = np.array(distance_features)
        
        return np.concatenate([normalized_coords, distance_array], axis=1)
    
    def _generate_text_embeddings(self, properties: List[PropertyData]) -> np.ndarray:
        """Generate text embeddings from property descriptions"""
        text_descriptions = []
        
        for prop in properties:
            # Create rich text description for embedding
            desc = f"{prop.property_type} in {prop.city}, {prop.state}. "
            desc += f"{prop.bedrooms} bedrooms, {prop.bathrooms} bathrooms, "
            desc += f"{prop.square_feet} sq ft. Built in {prop.year_built}. "
            
            if prop.neighborhood:
                desc += f"Located in {prop.neighborhood}. "
            
            features = []
            if prop.pool:
                features.append("pool")
            if prop.fireplace:
                features.append("fireplace")
            if prop.updated_kitchen:
                features.append("updated kitchen")
            if prop.updated_bathrooms:
                features.append("updated bathrooms")
                
            if features:
                desc += f"Features: {', '.join(features)}. "
            
            if prop.market_trend:
                desc += f"Market trend: {prop.market_trend}."
            
            text_descriptions.append(desc)
        
        return self.text_model.encode(text_descriptions)
    
    def generate_embeddings(self, properties: List[PropertyData]) -> Tuple[np.ndarray, Dict]:
        """
        Generate comprehensive embeddings for property comparables
        
        Args:
            properties: List of PropertyData objects
            
        Returns:
            Tuple of (embeddings array, metadata dict)
        """
        # Generate different types of embeddings
        numerical_emb = self._normalize_numerical_features(properties)
        categorical_emb = self._encode_categorical_features(properties)
        binary_emb = self._encode_binary_features(properties)
        location_emb = self._generate_location_embeddings(properties)
        text_emb = self._generate_text_embeddings(properties)
        
        # Combine embeddings with weights
        embeddings = np.concatenate([
            numerical_emb * self.feature_weights['numerical'],
            categorical_emb * self.feature_weights['categorical'],
            binary_emb * self.feature_weights['categorical'],
            location_emb * self.feature_weights['location'],
            text_emb * self.feature_weights['text']
        ], axis=1)
        
        # Generate metadata for each property
        metadata = []
        for i, prop in enumerate(properties):
            meta = {
                'zpid': prop.zpid,
                'address': prop.address,
                'city': prop.city,
                'state': prop.state,
                'price': prop.price,
                'bedrooms': prop.bedrooms,
                'bathrooms': prop.bathrooms,
                'square_feet': prop.square_feet,
                'property_type': prop.property_type,
                'sale_date': prop.sale_date.isoformat(),
                'price_per_sqft': prop.price_per_sqft,
                'latitude': prop.latitude,
                'longitude': prop.longitude,
                'embedding_id': hashlib.md5(f"{prop.zpid}_{prop.sale_date}".encode()).hexdigest()
            }
            metadata.append(meta)
        
        return embeddings, metadata
    
    def find_comparables(self, target_property: PropertyData, 
                        all_embeddings: np.ndarray, all_metadata: List[Dict],
                        top_k: int = 10, max_age_days: int = 180) -> List[Dict]:
        """
        Find comparable properties using vector similarity
        
        Args:
            target_property: Property to find comparables for
            all_embeddings: Pre-computed embeddings array
            all_metadata: Metadata for all properties
            top_k: Number of comparables to return
            max_age_days: Maximum age of comparable sales in days
            
        Returns:
            List of comparable properties with similarity scores
        """
        # Generate embedding for target property
        target_embedding, _ = self.generate_embeddings([target_property])
        target_vector = target_embedding[0]
        
        # Filter by recency
        cutoff_date = datetime.now() - timedelta(days=max_age_days)
        valid_indices = []
        
        for i, meta in enumerate(all_metadata):
            sale_date = datetime.fromisoformat(meta['sale_date'])
            if sale_date >= cutoff_date:
                valid_indices.append(i)
        
        if not valid_indices:
            return []
        
        # Calculate similarities
        valid_embeddings = all_embeddings[valid_indices]
        similarities = np.dot(valid_embeddings, target_vector) / (
            np.linalg.norm(valid_embeddings, axis=1) * np.linalg.norm(target_vector)
        )
        
        # Get top K similar properties
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        comparables = []
        for idx in top_indices:
            original_idx = valid_indices[idx]
            comparable = all_metadata[original_idx].copy()
            comparable['similarity_score'] = float(similarities[idx])
            comparables.append(comparable)
        
        return comparables

# Example usage and vector database integration
class VectorDBManager:
    """Example integration with vector databases like Pinecone, Weaviate, or Chroma"""
    
    def __init__(self, db_type: str = "chroma"):
        self.db_type = db_type
        self.embedding_generator = ZillowEmbeddingGenerator()
    
    def store_properties(self, properties: List[PropertyData]):
        """Store properties in vector database"""
        embeddings, metadata = self.embedding_generator.generate_embeddings(properties)
        
        if self.db_type == "chroma":
            # Example Chroma integration
            import chromadb
            client = chromadb.Client()
            collection = client.create_collection("zillow_comparables")
            
            ids = [meta['embedding_id'] for meta in metadata]
            collection.add(
                embeddings=embeddings.tolist(),
                metadatas=metadata,
                ids=ids
            )
        
        elif self.db_type == "pinecone":
            # Example Pinecone integration
            import pinecone
            
            # Initialize Pinecone (requires API key)
            # pinecone.init(api_key="your-api-key", environment="your-env")
            # index = pinecone.Index("zillow-comparables")
            
            vectors = [(meta['embedding_id'], emb.tolist(), meta) 
                      for emb, meta in zip(embeddings, metadata)]
            # index.upsert(vectors=vectors)
    
    def query_comparables(self, target_property: PropertyData, top_k: int = 10):
        """Query for comparable properties"""
        target_embedding, _ = self.embedding_generator.generate_embeddings([target_property])
        
        if self.db_type == "chroma":
            import chromadb
            client = chromadb.Client()
            collection = client.get_collection("zillow_comparables")
            
            results = collection.query(
                query_embeddings=target_embedding.tolist(),
                n_results=top_k
            )
            return results
        
        # Add other database implementations as needed

# Example data preparation
def create_sample_properties() -> List[PropertyData]:
    """Create sample property data for testing"""
    sample_data = [
        PropertyData(
            zpid="12345",
            address="123 Main St",
            city="Seattle",
            state="WA",
            zip_code="98101",
            price=750000,
            bedrooms=3,
            bathrooms=2.5,
            square_feet=2000,
            lot_size=0.25,
            year_built=2015,
            property_type="Single Family",
            sale_date=datetime(2024, 1, 15),
            days_on_market=30,
            price_per_sqft=375,
            latitude=47.6062,
            longitude=-122.3321,
            neighborhood="Capitol Hill",
            school_district="Seattle Public Schools",
            garage_spaces=2,
            stories=2,
            pool=False,
            fireplace=True,
            updated_kitchen=True,
            updated_bathrooms=False,
            market_trend="Hot",
            listing_views=1250
        ),
        # Add more sample properties as needed
    ]
    return sample_data

if __name__ == "__main__":
    # Example usage
    properties = create_sample_properties()
    
    # Generate embeddings
    generator = ZillowEmbeddingGenerator()
    embeddings, metadata = generator.generate_embeddings(properties)
    
    print(f"Generated embeddings shape: {embeddings.shape}")
    print(f"Sample metadata keys: {list(metadata[0].keys())}")
    
    # Example vector database storage
    db_manager = VectorDBManager()
    # db_manager.store_properties(properties)
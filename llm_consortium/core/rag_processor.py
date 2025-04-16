# from pathlib import Path
# from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
# from llama_index.core.storage import StorageContext
# from llama_index.vector_stores.qdrant import QdrantVectorStore
# import qdrant_client

# class RAGProcessor:
#     def __init__(self, data_dir="data"):
#         self.data_dir = Path(data_dir)
#         self.raw_files_dir = self.data_dir / "raw_files"
#         self.processed_dir = self.data_dir / "processed"
        
#         # Create directories if they don't exist
#         self.raw_files_dir.mkdir(parents=True, exist_ok=True)
#         self.processed_dir.mkdir(parents=True, exist_ok=True)
        
#         # Initialize vector store
#         self.client = qdrant_client.QdrantClient(path="qdrant_db")
#         self.vector_store = QdrantVectorStore(client=self.client, collection_name="consortium_rag")
#         self.storage_context = StorageContext.from_defaults(vector_store=self.vector_store)

#     def process_uploaded_file(self, uploaded_file):
#         """Save and process uploaded files"""
#         # Save original file
#         save_path = self.raw_files_dir / uploaded_file.name
#         with open(save_path, "wb") as f:
#             f.write(uploaded_file.getbuffer())
        
#         # Process file into text chunks
#         # Add custom processing for different file types here
#         documents = SimpleDirectoryReader(input_dir=str(self.raw_files_dir)).load_data()
        
#         # Create/update vector index
#         index = VectorStoreIndex.from_documents(
#             documents,
#             storage_context=self.storage_context
#         )
#         return index










# # Anmol code#

# import os
# import qdrant_client
# from dotenv import load_dotenv
# from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext
# from llama_index.core.vector_stores.qdrant import QdrantVectorStore
# from llama_index.embeddings.fastembed import FastEmbedEmbedding
# from llama_index.core import Settings
# from qdrant_client.http.models import Distance, VectorParams

# # Load environment variables
# load_dotenv()

# class RAGHandler:
#     def __init__(self):

#         self.qdrant_api_key = os.getenv("QDRANT_API_KEY")
#         self.qdrant_url = os.getenv("QDRANT_URL")
#         self.collection_name = os.getenv("document_embeddings_store")

#         if not all([self.qdrant_api_key, self.qdrant_url, self.collection_name]):
#             raise ValueError("Missing required environment variables")

#         # Set the embedding model
#         Settings.embed_model = FastEmbedEmbedding(model_name="BAAI/bge-base-en-v1.5")

#         # Initialize Qdrant client with timeout
#         self.q_client = qdrant_client.QdrantClient(
#             api_key=self.qdrant_api_key,
#             url=self.qdrant_url,
#             timeout=30  # Add timeout for connection
#         )

#         # Load documents
#         try:
#             self.documents = SimpleDirectoryReader("data").load_data()
#         except Exception as e:
#             raise FileNotFoundError(f"Error loading documents: {str(e)}")
        
#         # Check if collection exists, otherwise create it
#         self._ensure_collection_exists()

#         # Set up vector store
#         self.vector_store = QdrantVectorStore(
#             client=self.q_client,
#             collection_name=self.collection_name,
#             prefer_grpc=True # Better for production
#         )

#         # Create storage context
#         self.storage_context = StorageContext.from_defaults(vector_store=self.vector_store)

#         # Create index
#         self.index = VectorStoreIndex.from_documents(
#             self.documents,
#             storage_context=self.storage_context,
#             show_progress=True # Add progress tracking
#         )

#         # Initialize query engine
#         self.query_engine = self.index.as_query_engine()

#     def _ensure_collection_exists(self):
#         """Check if the Qdrant collection exists, and create it if not."""
#         try :
#             collections = self.q_client.get_collections()
#             collection_names = {c.name for c in collections.collections}

#             if self.collection_name not in collection_names:
#                 print(f"Collection '{self.collection_name}' does not exist. Creating a new one...")
#                 self.q_client.create_collection(
#                     collection_name=self.collection_name,
#                     vectors_config=VectorParams(size=768, distance=Distance.COSINE)  # Adjust size based on the embedding model
#                 )
#         except Exception as e:
#                 raise ConnectionError(f"Qdrant connection failed: {str(e)}")

#     def get_context(self, prompt: str) -> str:
#         """Retrieve context based on the given prompt"""
#         try:
#             response = self.query_engine.query(prompt)
#             return str(response)
#         except Exception as e:
#             return f"Error retrieving context: {str(e)}"
















# import os
# from pathlib import Path
# from typing import Optional
# import qdrant_client
# from dotenv import load_dotenv
# from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext, Settings
# from llama_index.vector_stores.qdrant import QdrantVectorStore
# from llama_index.embeddings.fastembed import FastEmbedEmbedding
# from qdrant_client.http import models as qdrant_models

# # Load environment variables once at startup
# load_dotenv()

# class RAGConfig:
#     """Central configuration class for RAG parameters"""
#     def __init__(self):
#         # Environment variables
#         self.qdrant_api_key = os.getenv("QDRANT_API_KEY")
#         self.qdrant_url = os.getenv("QDRANT_URL")
#         self.collection_name = os.getenv("DOCUMENT_EMBEDDINGS_STORE", "default_rag_collection")
        
#         # File paths
#         self.data_dir = Path("data")
#         self.raw_files_dir = self.data_dir / "raw_files"
#         self.processed_dir = self.data_dir / "processed"
        
#         # Model parameters
#         self.embed_model_name = "BAAI/bge-base-en-v1.5"
#         self.embedding_dim = 768  # Must match model output
#         self.distance_metric = qdrant_models.Distance.COSINE
        
#         # Qdrant parameters
#         self.qdrant_timeout = 30
#         self.prefer_grpc = True

# class RAGSystem:
#     """Unified RAG system handling both file processing and querying"""
#     def __init__(self, config: Optional[RAGConfig] = None):
#         self.config = config or RAGConfig()
#         self._setup_directories()
#         self._initialize_components()
        
#     def _setup_directories(self):
#         """Ensure required directory structure exists"""
#         self.config.raw_files_dir.mkdir(parents=True, exist_ok=True)
#         self.config.processed_dir.mkdir(parents=True, exist_ok=True)

#     def _initialize_components(self):
#         """Initialize core RAG components"""
#         self._validate_environment()
#         self._setup_embedding_model()
#         self.qdrant_client = self._create_qdrant_client()
#         self.vector_store = self._create_vector_store()
#         self._ensure_collection_exists()

#     def _validate_environment(self):
#         """Validate required environment variables"""
#         if not all([self.config.qdrant_api_key, self.config.qdrant_url]):
#             raise ValueError("Missing Qdrant API credentials in environment variables")

#     def _setup_embedding_model(self):
#         """Configure the embedding model"""
#         Settings.embed_model = FastEmbedEmbedding(
#             model_name=self.config.embed_model_name
#         )

#     def _create_qdrant_client(self) -> qdrant_client.QdrantClient:
#         """Create and return Qdrant client with error handling"""
#         return qdrant_client.QdrantClient(
#             api_key=self.config.qdrant_api_key,
#             url=self.config.qdrant_url,
#             timeout=self.config.qdrant_timeout,
#             prefer_grpc=self.config.prefer_grpc
#         )

#     def _create_vector_store(self) -> QdrantVectorStore:
#         """Create Qdrant vector store instance"""
#         return QdrantVectorStore(
#             client=self.qdrant_client,
#             collection_name=self.config.collection_name
#         )

#     def _ensure_collection_exists(self):
#         """Ensure Qdrant collection exists with proper configuration"""
#         try:
#             collections = self.qdrant_client.get_collections()
#             if self.config.collection_name not in {c.name for c in collections.collections}:
#                 self._create_collection()
#         except Exception as e:
#             raise ConnectionError(f"Qdrant connection failed: {str(e)}")

#     def _create_collection(self):
#         """Create new Qdrant collection with proper vector configuration"""
#         self.qdrant_client.create_collection(
#             collection_name=self.config.collection_name,
#             vectors_config=qdrant_models.VectorParams(
#                 size=self.config.embedding_dim,
#                 distance=self.config.distance_metric
#             )
#         )

#     def process_documents(self, input_dir: Optional[str] = None) -> VectorStoreIndex:
#         """Process documents from specified directory"""
#         input_path = Path(input_dir) if input_dir else self.config.raw_files_dir
        
#         try:
#             documents = SimpleDirectoryReader(input_dir=str(input_path)).load_data()
#             return VectorStoreIndex.from_documents(
#                 documents,
#                 storage_context=StorageContext.from_defaults(
#                     vector_store=self.vector_store
#                 ),
#                 show_progress=True
#             )
#         except Exception as e:
#             raise RuntimeError(f"Document processing failed: {str(e)}")

#     def query(self, prompt: str, index: Optional[VectorStoreIndex] = None) -> str:
#         """Execute query against RAG system"""
#         try:
#             query_engine = (index or self.index).as_query_engine()
#             response = query_engine.query(prompt)
#             return str(response)
#         except AttributeError:
#             raise RuntimeError("Index not initialized - process documents first")
#         except Exception as e:
#             return f"Query failed: {str(e)}"

#     def upload_file(self, uploaded_file):
#         """Handle file uploads and immediate processing"""
#         save_path = self.config.raw_files_dir / uploaded_file.name
#         with open(save_path, "wb") as f:
#             f.write(uploaded_file.getbuffer())
#         return self.process_documents()




















import os
from pathlib import Path
from typing import Optional
import qdrant_client
from charset_normalizer import from_bytes
from llama_index.readers.file import DocxReader, PDFReader
from llama_index.core.readers.base import BaseReader
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext, Document, Settings
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.embeddings.fastembed import FastEmbedEmbedding
from qdrant_client.http import models as qdrant_models
from dotenv import load_dotenv


# Load environment variables once at startup
load_dotenv()


class CustomTextReader(BaseReader):
    """Text file reader with encoding detection"""
    def load_data(self, file_path, extra_info=None):
        try:
            # Convert Path to string early
            file_path_str = str(file_path)
        
            with open(file_path, "rb") as f:
                raw_data = f.read()
            
            # Detect encoding
            result = from_bytes(raw_data)
            best_guess = result.best()
            
            if not best_guess:
                raise ValueError(f"Couldn't detect encoding for {file_path_str}")
            
            return [Document(text=str(best_guess), metadata={"filename": file_path_str, "file_path": file_path_str})]
            
        except Exception as e:
            raise ValueError(f"Error reading {file_path}: {str(e)}")

class RAGConfig:
    """Central configuration class for RAG parameters"""
    def __init__(self):
        # Environment variables
        self.qdrant_api_key = os.getenv("QDRANT_API_KEY")
        self.qdrant_url = os.getenv("QDRANT_URL")
        self.collection_name = os.getenv("DOCUMENT_EMBEDDINGS_STORE", "default_rag_collection")
        
        # File paths
        self.data_dir = Path("data")
        self.raw_files_dir = self.data_dir / "raw_files"
        self.processed_dir = self.data_dir / "processed"
        
        # Model parameters
        self.embed_model_name = "BAAI/bge-base-en-v1.5"
        self.embedding_dim = 768  # Must match model output
        self.distance_metric = qdrant_models.Distance.COSINE
        
        # Qdrant parameters
        self.qdrant_timeout = 30
        self.prefer_grpc = True

class RAGSystem:
    """Unified RAG system handling both file processing and querying"""
    def __init__(self, config: Optional[RAGConfig] = None):
        self.config = config or RAGConfig()
        self.index = None
        self._setup_directories()
        self._initialize_components()
        
    def _setup_directories(self):
        """Ensure required directory structure exists"""
        self.config.raw_files_dir.mkdir(parents=True, exist_ok=True)
        self.config.processed_dir.mkdir(parents=True, exist_ok=True)

    def _initialize_components(self):
        """Initialize core RAG components"""
        self._validate_environment()
        self._setup_embedding_model()
        self.qdrant_client = self._create_qdrant_client()
        self.vector_store = self._create_vector_store()
        self._ensure_collection_exists()

    def _validate_environment(self):
        """Validate required environment variables"""
        if not all([self.config.qdrant_api_key, self.config.qdrant_url]):
            raise ValueError("Missing Qdrant API credentials in environment variables")

    def _setup_embedding_model(self):
        """Configure the embedding model"""
        Settings.embed_model = FastEmbedEmbedding(
            model_name=self.config.embed_model_name
        )

    def _create_qdrant_client(self) -> qdrant_client.QdrantClient:
        """Create and return Qdrant client with error handling"""
        return qdrant_client.QdrantClient(
            api_key=self.config.qdrant_api_key,
            url=self.config.qdrant_url,
            timeout=self.config.qdrant_timeout,
            prefer_grpc=self.config.prefer_grpc
        )

    def _create_vector_store(self) -> QdrantVectorStore:
        """Create Qdrant vector store instance"""
        return QdrantVectorStore(
            client=self.qdrant_client,
            collection_name=self.config.collection_name
        )

    def _ensure_collection_exists(self):
        """Ensure Qdrant collection exists with proper configuration"""
        try:
            collections = self.qdrant_client.get_collections()
            if self.config.collection_name not in {c.name for c in collections.collections}:
                self._create_collection()
        except Exception as e:
            raise ConnectionError(f"Qdrant connection failed: {str(e)}")

    def _create_collection(self):
        """Create new Qdrant collection with proper vector configuration"""
        self.qdrant_client.create_collection(
            collection_name=self.config.collection_name,
            vectors_config=qdrant_models.VectorParams(
                size=self.config.embedding_dim,
                distance=self.config.distance_metric
            )
        )

    def process_documents(self, input_dir: Optional[str] = None) -> VectorStoreIndex:
        """Process documents from specified directory"""
        input_path = Path(input_dir) if input_dir else self.config.raw_files_dir
        
        try:
            # Create sanitized file extractors
            def create_sanitized_extractor(reader):
                def wrapper(file_path):
                    docs = reader.load_data(file_path)
                    for doc in docs:
                        doc.metadata = {
                            k: str(v) if isinstance(v, Path) else v
                            for k, v in doc.metadata.items()
                        }
                    return docs
                return wrapper

            file_extractor = {
                ".txt": create_sanitized_extractor(CustomTextReader()),
                ".md": create_sanitized_extractor(CustomTextReader()),
                ".pdf": create_sanitized_extractor(PDFReader()),
                ".docx": create_sanitized_extractor(DocxReader()),
                ".csv": CustomTextReader(),
                ".json": CustomTextReader(),
                ".xml": CustomTextReader(),
                ".html": CustomTextReader()
                # Add other text formats here
            }
            documents = SimpleDirectoryReader(input_dir=str(input_path),file_extractor=file_extractor).load_data()
            return VectorStoreIndex.from_documents(
                documents,
                storage_context=StorageContext.from_defaults(
                    vector_store=self.vector_store
                ),
                show_progress=True
            )
        except Exception as e:
            raise RuntimeError(f"Document processing failed: {str(e)}")

    def query(self, prompt: str) -> str:
        """Execute query against RAG system"""
        try:
            if not self.index:
                raise RuntimeError("Index not initialized - process documents first")
            
            query_engine = self.index.as_query_engine()
            response = query_engine.query(prompt)
            return str(response)
        except Exception as e:
            return f"Query failed: {str(e)}"

    def upload_file(self, uploaded_file):
        """Handle file uploads and immediate processing"""
        save_path = self.config.raw_files_dir / uploaded_file.name
        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        self.index = self.process_documents()
        return self.index
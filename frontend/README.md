# RAG System Frontend

A modern React frontend for the RAG (Retrieval-Augmented Generation) system with TypeScript and Tailwind CSS.

## Features

- **Query Interface**: Submit queries to the RAG system and view responses with confidence scores and sources
- **Experiment Management**: Start and monitor RAG experiments (sample and comprehensive modes)
- **Document Management**: Upload, list, and delete documents for the RAG system
- **Evaluation Management**: Upload and manage JSON evaluation files
- **Dashboard**: View system statistics and query history

## API Integration

The frontend integrates with the following API endpoints:

### Query RAG
- `POST /query` - Submit queries to the RAG system

### Experiments
- `POST /experiments/start` - Start new experiments
- `GET /experiments` - List all experiments
- `GET /experiments/{job_id}` - Get experiment status
- `GET /experiments/{job_id}/results` - Get experiment results

### Documents
- `POST /documents/upload` - Upload documents
- `GET /documents` - List documents
- `DELETE /documents/{filename}` - Delete documents

### Evaluation
- `POST /evaluation/upload` - Upload evaluation files
- `GET /evaluation` - List evaluation files
- `DELETE /evaluation/{filename}` - Delete evaluation files

### Stats and History
- `GET /stats` - Get system statistics
- `GET /history` - Get query history
- `DELETE /history` - Clear query history

## Installation

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm start
```

3. Open [http://localhost:3000](http://localhost:3000) to view the application.

## Configuration

The frontend is configured to connect to the RAG API at `http://localhost:8000`. To change this, update the `API_BASE_URL` in `src/services/api.ts`.

## Technologies Used

- React 18 with TypeScript
- Tailwind CSS for styling
- Axios for API communication
- Lucide React for icons

## Project Structure

```
src/
├── components/          # React components
│   ├── QueryInterface.tsx
│   ├── QueryResponse.tsx
│   ├── ExperimentManager.tsx
│   ├── DocumentManager.tsx
│   ├── EvaluationManager.tsx
│   └── Dashboard.tsx
├── services/
│   └── api.ts          # API client
├── types/
│   └── index.ts        # TypeScript type definitions
├── App.tsx             # Main application component
├── index.tsx           # Application entry point
└── index.css           # Global styles
```

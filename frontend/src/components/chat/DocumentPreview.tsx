import React, { useState, useEffect, useCallback } from 'react';
import { X, FileText, Clock, Link2, TrendingUp } from 'lucide-react';
import { chatAPI } from '../../api/client';

interface DocumentPreviewProps {
  documentId: number;
  onClose: () => void;
}

const DocumentPreview: React.FC<DocumentPreviewProps> = ({ documentId, onClose }) => {
  const [document, setDocument] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'content' | 'usage'>('content');

  const loadDocument = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await chatAPI.previewDocument(documentId);
      setDocument(data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to load document');
    } finally {
      setLoading(false);
    }
  }, [documentId]);

  useEffect(() => {
    loadDocument();
  }, [loadDocument]);

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
  };

  const highlightMatchedContent = (content: string, matches: any[]) => {
    if (!matches || matches.length === 0) return content;

    let highlightedContent = content;
    const matchedSnippets = matches
      .map(m => m.matched_content)
      .filter(Boolean)
      .sort((a, b) => b.length - a.length); // Sort by length descending

    matchedSnippets.forEach((snippet, index) => {
      // Escape special regex characters
      const escapedSnippet = snippet.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
      const regex = new RegExp(escapedSnippet, 'gi');

      // Use a unique marker that won't appear in text
      const marker = `__HIGHLIGHT_${index}__`;
      highlightedContent = highlightedContent.replace(regex, marker);
    });

    // Replace markers with HTML
    matchedSnippets.forEach((snippet, index) => {
      const marker = `__HIGHLIGHT_${index}__`;
      highlightedContent = highlightedContent.replace(
        new RegExp(marker, 'g'),
        `<mark class="bg-yellow-200 dark:bg-yellow-700 px-1 rounded">${snippet}</mark>`
      );
    });

    return highlightedContent;
  };

  if (loading) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl p-8 max-w-4xl w-full mx-4">
          <div className="flex items-center justify-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl p-8 max-w-4xl w-full mx-4">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-bold text-red-600">Error</h2>
            <button onClick={onClose} className="text-gray-500 hover:text-gray-700">
              <X className="w-6 h-6" />
            </button>
          </div>
          <p className="text-gray-700 dark:text-gray-300">{error}</p>
        </div>
      </div>
    );
  }

  if (!document) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-4xl w-full max-h-[90vh] flex flex-col">
        {/* Header */}
        <div className="flex justify-between items-start p-6 border-b border-gray-200 dark:border-gray-700">
          <div className="flex-1">
            <div className="flex items-center gap-3">
              <FileText className="w-6 h-6 text-blue-500" />
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                {document.filename}
              </h2>
            </div>
            <div className="mt-2 flex items-center gap-4 text-sm text-gray-600 dark:text-gray-400">
              <div className="flex items-center gap-1">
                <Clock className="w-4 h-4" />
                <span>{formatDate(document.created_at)}</span>
              </div>
              <div className="flex items-center gap-1">
                <Link2 className="w-4 h-4" />
                <span>{document.usage_count} references</span>
              </div>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 dark:hover:text-gray-300 ml-4"
          >
            <X className="w-6 h-6" />
          </button>
        </div>

        {/* Tabs */}
        <div className="flex border-b border-gray-200 dark:border-gray-700 px-6">
          <button
            onClick={() => setActiveTab('content')}
            className={`px-4 py-3 font-medium border-b-2 transition-colors ${
              activeTab === 'content'
                ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                : 'border-transparent text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
            }`}
          >
            <div className="flex items-center gap-2">
              <FileText className="w-4 h-4" />
              Content
            </div>
          </button>
          <button
            onClick={() => setActiveTab('usage')}
            className={`px-4 py-3 font-medium border-b-2 transition-colors ${
              activeTab === 'usage'
                ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                : 'border-transparent text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
            }`}
          >
            <div className="flex items-center gap-2">
              <TrendingUp className="w-4 h-4" />
              Usage History ({document.usage_count})
            </div>
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {activeTab === 'content' ? (
            <div className="prose dark:prose-invert max-w-none">
              <div
                className="whitespace-pre-wrap text-sm text-gray-800 dark:text-gray-200 font-mono bg-gray-50 dark:bg-gray-900 p-4 rounded-lg"
                dangerouslySetInnerHTML={{
                  __html: highlightMatchedContent(document.content || '', document.recent_matches || []),
                }}
              />
              {document.recent_matches && document.recent_matches.length > 0 && (
                <div className="mt-4 p-4 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg border border-yellow-200 dark:border-yellow-800">
                  <p className="text-sm text-yellow-800 dark:text-yellow-200">
                    <strong>Highlighted sections</strong> show content that was used to answer questions.
                  </p>
                </div>
              )}
            </div>
          ) : (
            <div className="space-y-4">
              {document.recent_matches && document.recent_matches.length > 0 ? (
                <>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    Recent questions answered using this document:
                  </p>
                  {document.recent_matches.map((match: any, index: number) => (
                    <div
                      key={index}
                      className="bg-gray-50 dark:bg-gray-900 p-4 rounded-lg border border-gray-200 dark:border-gray-700"
                    >
                      <div className="flex items-start gap-3">
                        <div className="flex-shrink-0 w-8 h-8 bg-blue-100 dark:bg-blue-900 rounded-full flex items-center justify-center">
                          <span className="text-blue-600 dark:text-blue-300 text-sm font-medium">
                            {index + 1}
                          </span>
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="text-sm text-gray-900 dark:text-gray-100 mb-2">
                            <strong>Question:</strong> {match.message_content}
                          </div>
                          {match.matched_content && (
                            <div className="text-xs text-gray-600 dark:text-gray-400 bg-yellow-50 dark:bg-yellow-900/20 p-2 rounded border-l-4 border-yellow-400">
                              <strong>Matched content:</strong> {match.matched_content}
                            </div>
                          )}
                          <div className="mt-2 flex items-center gap-4 text-xs text-gray-500 dark:text-gray-500">
                            <span>Relevance: {match.relevance_score}</span>
                            <span>{formatDate(match.created_at)}</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </>
              ) : (
                <div className="text-center py-8">
                  <TrendingUp className="w-12 h-12 text-gray-400 mx-auto mb-3" />
                  <p className="text-gray-600 dark:text-gray-400">
                    This document hasn't been used to answer any questions yet.
                  </p>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex justify-end p-6 border-t border-gray-200 dark:border-gray-700">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-200 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

export default DocumentPreview;


import React from 'react';
import { Cpu } from 'lucide-react';

interface ModelSelectorProps {
  selectedProvider: string;
  availableProviders: any;
  onProviderChange: (provider: string) => void;
}

const ModelSelector: React.FC<ModelSelectorProps> = ({
  selectedProvider,
  availableProviders,
  onProviderChange,
}) => {
  const providers = Object.keys(availableProviders);

  return (
    <div className="flex items-center space-x-3 bg-white/50 rounded-xl px-4 py-2 border border-gray-200 shadow-sm">
      <Cpu className="h-4 w-4 text-indigo-600" />
      <select
        id="provider-select"
        value={selectedProvider}
        onChange={(e) => onProviderChange(e.target.value)}
        className="block bg-transparent border-0 text-sm font-medium text-gray-700 focus:outline-none focus:ring-0 cursor-pointer"
      >
        <option value="default">Auto Select</option>
        {providers.map((provider) => (
          <option key={provider} value={provider}>
            {provider} • {availableProviders[provider]?.model || 'Unknown'}
          </option>
        ))}
      </select>
    </div>
  );
};

export default ModelSelector;
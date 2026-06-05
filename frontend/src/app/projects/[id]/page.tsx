'use client';

import { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardHeader, CardTitle, CardContent, CardFooter } from '@/components/ui/card';
import api from '@/lib/api';
import { toast } from 'sonner';

export default function ProjectPage() {
  const { id: projectId } = useParams();
  const [prompt, setPrompt] = useState('');
  const [secret, setSecret] = useState('');
  const [chatHistory, setChatHistory] = useState<{role: string, content: string}[]>([]);
  const [loading, setLoading] = useState(false);
  const [files, setFiles] = useState<any[]>([]);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const router = useRouter();

  useEffect(() => {
    // We would fetch file history here if we wanted
  }, [projectId]);

  const handleUpload = async () => {
    if (!selectedFile || !secret) {
      toast.error('File and secret required');
      return;
    }
    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('secret', secret);
    
    try {
      setLoading(true);
      await api.post(`/chat/${projectId}/upload`, formData);
      toast.success('File uploaded and indexed');
      setSelectedFile(null);
    } catch (err) {
      toast.error('Upload failed');
    } finally {
      setLoading(false);
    }
  };

  const handleQuery = async () => {
    if (!prompt || !secret) {
      toast.error('Prompt and secret required');
      return;
    }
    
    setChatHistory([...chatHistory, { role: 'user', content: prompt }]);
    setLoading(true);
    setPrompt('');
    
    try {
      const res = await api.post(`/chat/${projectId}/query`, { prompt, secret });
      setChatHistory(prev => [...prev, { role: 'bot', content: res.data.response }]);
    } catch (err) {
      toast.error('Query failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-8 max-w-4xl mx-auto h-screen flex flex-col">
      <div className="flex justify-between items-center mb-4">
        <h1 className="text-2xl font-bold">RAG Chatbot</h1>
        <div className="flex gap-2">
          <Input 
            type="password" 
            placeholder="Enter secret to chat/upload" 
            value={secret} 
            onChange={(e) => setSecret(e.target.value)}
            className="w-48"
          />
        </div>
      </div>

      <div className="grid grid-cols-4 gap-4 flex-1 overflow-hidden">
        <Card className="col-span-1 p-4 overflow-y-auto">
          <h3 className="font-bold mb-4">Index Files</h3>
          <div className="space-y-4">
            <Input type="file" onChange={(e) => setSelectedFile(e.target.files?.[0] || null)} />
            <Button onClick={handleUpload} disabled={loading || !selectedFile} className="w-full">
              {loading ? 'Uploading...' : 'Upload & Index'}
            </Button>
          </div>
        </Card>

        <Card className="col-span-3 flex flex-col overflow-hidden">
          <CardHeader>
            <CardTitle>Chat</CardTitle>
          </CardHeader>
          <CardContent className="flex-1 overflow-y-auto space-y-4 p-4">
            {chatHistory.length === 0 && <p className="text-gray-400 text-center mt-8">Start a conversation...</p>}
            {chatHistory.map((msg, i) => (
              <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`max-w-[80%] p-3 rounded-lg ${msg.role === 'user' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-black'}`}>
                  {msg.content}
                </div>
              </div>
            ))}
            {loading && <p className="text-gray-400 italic">Thinking...</p>}
          </CardContent>
          <CardFooter className="p-4 border-t">
            <div className="flex w-full gap-2">
              <Input placeholder="Ask about your files..." value={prompt} onChange={(e) => setPrompt(e.target.value)} onKeyDown={(e) => e.key === 'Enter' && handleQuery()} />
              <Button onClick={handleQuery} disabled={loading}>Send</Button>
            </div>
          </CardFooter>
        </Card>
      </div>
    </div>
  );
}

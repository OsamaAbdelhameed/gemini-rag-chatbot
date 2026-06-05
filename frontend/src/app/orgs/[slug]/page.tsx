'use client';

import { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import api from '@/lib/api';
import { toast } from 'sonner';
import { encryptGeminiKey } from '@/lib/encryption';

export default function OrgPage() {
  const { slug: orgId } = useParams();
  const [projects, setProjects] = useState<any[]>([]);
  const [members, setMembers] = useState<any[]>([]);
  const [newProjectName, setNewProjectName] = useState('');
  const [geminiKey, setGeminiKey] = useState('');
  const [secret, setSecret] = useState('');
  const [memberEmail, setMemberEmail] = useState('');
  const router = useRouter();

  useEffect(() => {
    if (orgId) {
      fetchProjects();
      fetchMembers();
    }
  }, [orgId]);

  const fetchProjects = async () => {
    try {
      const res = await api.get(`/projects/${orgId}`);
      setProjects(res.data);
    } catch (err) {
      toast.error('Failed to fetch projects');
    }
  };

  const fetchMembers = async () => {
    try {
      const res = await api.get(`/orgs/${orgId}/members`);
      setMembers(res.data);
    } catch (err) {
      toast.error('Failed to fetch members');
    }
  };

  const createProject = async () => {
    try {
      const encryptedKey = encryptGeminiKey(geminiKey, secret);
      await api.post('/projects/', { 
        name: newProjectName, 
        org_id: parseInt(orgId as string),
        gemini_api_key_encrypted: encryptedKey
      });
      toast.success('Project created');
      fetchProjects();
      setNewProjectName('');
      setGeminiKey('');
      setSecret('');
    } catch (err) {
      toast.error('Failed to create project');
    }
  };

  const addMember = async () => {
    try {
      await api.post(`/orgs/${orgId}/members`, { email: memberEmail });
      toast.success('Member added');
      fetchMembers();
      setMemberEmail('');
    } catch (err) {
      toast.error('Failed to add member');
    }
  };

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <Button variant="ghost" className="mb-4" onClick={() => router.push('/dashboard')}>← Back to Dashboard</Button>
      
      <Tabs defaultValue="projects">
        <TabsList className="mb-8">
          <TabsTrigger value="projects">Projects</TabsTrigger>
          <TabsTrigger value="members">Members</TabsTrigger>
        </TabsList>

        <TabsContent value="projects">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-2xl font-bold">Projects</h2>
            <Dialog>
              <DialogTrigger asChild>
                <Button>New Project</Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>New RAG Chatbot Project</DialogTitle>
                </DialogHeader>
                <div className="space-y-4 pt-4">
                  <Input placeholder="Project Name" value={newProjectName} onChange={(e) => setNewProjectName(e.target.value)} />
                  <Input placeholder="Gemini API Key" type="password" value={geminiKey} onChange={(e) => setGeminiKey(e.target.value)} />
                  <Input placeholder="Secret for Encryption (Must remember this!)" type="password" value={secret} onChange={(e) => setSecret(e.target.value)} />
                  <p className="text-xs text-gray-500">Your API key is encrypted on your machine and only decrypted in the backend memory during calls.</p>
                  <Button onClick={createProject} className="w-full">Create Project</Button>
                </div>
              </DialogContent>
            </Dialog>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {projects.map((p) => (
              <Card key={p.id} className="cursor-pointer hover:shadow-md transition-shadow" onClick={() => router.push(`/projects/${p.id}`)}>
                <CardHeader>
                  <CardTitle>{p.name}</CardTitle>
                </CardHeader>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="members">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-2xl font-bold">Members</h2>
            <div className="flex gap-2">
              <Input placeholder="Member Email" value={memberEmail} onChange={(e) => setMemberEmail(e.target.value)} />
              <Button onClick={addMember}>Add</Button>
            </div>
          </div>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Email</TableHead>
                <TableHead>Name</TableHead>
                <TableHead>Role</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {members.map((m, i) => (
                <TableRow key={i}>
                  <TableCell>{m.email}</TableCell>
                  <TableCell>{m.full_name}</TableCell>
                  <TableCell className="capitalize">{m.role}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TabsContent>
      </Tabs>
    </div>
  );
}

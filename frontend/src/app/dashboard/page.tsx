'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import api from '@/lib/api';
import { toast } from 'sonner';

export default function DashboardPage() {
  const [orgs, setOrgs] = useState<any[]>([]);
  const [newOrgName, setNewOrgName] = useState('');
  const [newOrgSlug, setNewOrgSlug] = useState('');
  const router = useRouter();

  useEffect(() => {
    fetchOrgs();
  }, []);

  const fetchOrgs = async () => {
    try {
      const res = await api.get('/orgs/');
      setOrgs(res.data);
    } catch (err) {
      toast.error('Failed to fetch organizations');
    }
  };

  const createOrg = async () => {
    try {
      await api.post('/orgs/', { name: newOrgName, slug: newOrgSlug });
      toast.success('Organization created');
      fetchOrgs();
      setNewOrgName('');
      setNewOrgSlug('');
    } catch (err) {
      toast.error('Failed to create organization');
    }
  };

  return (
    <div className="p-8 max-w-4xl mx-auto">
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold">Organizations</h1>
        <Dialog>
          <DialogTrigger asChild>
            <Button>Create Organization</Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>New Organization</DialogTitle>
            </DialogHeader>
            <div className="space-y-4 pt-4">
              <Input placeholder="Org Name" value={newOrgName} onChange={(e) => setNewOrgName(e.target.value)} />
              <Input placeholder="Slug (unique)" value={newOrgSlug} onChange={(e) => setNewOrgSlug(e.target.value)} />
              <Button onClick={createOrg} className="w-full">Create</Button>
            </div>
          </DialogContent>
        </Dialog>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {orgs.map((org) => (
          <Card key={org.id} className="cursor-pointer hover:shadow-md transition-shadow" onClick={() => router.push(`/orgs/${org.id}`)}>
            <CardHeader>
              <CardTitle>{org.name}</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-gray-500">Slug: {org.slug}</p>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}

import '@testing-library/jest-dom';
import { vi } from 'vitest';
import React from 'react';

// Mock Next.js router
vi.mock('next/router', () => ({
  useRouter() {
    return {
      route: '/',
      pathname: '/',
      query: '',
      asPath: '',
      push: vi.fn(),
      pop: vi.fn(),
      reload: vi.fn(),
      back: vi.fn(),
      prefetch: vi.fn(),
      beforePopState: vi.fn(),
      events: {
        on: vi.fn(),
        off: vi.fn(),
        emit: vi.fn(),
      },
    };
  },
}));

// Mock Next.js image
vi.mock('next/image', () => ({
  __esModule: true,
  default: (props: any) => React.createElement('img', props),
}));

// Mock lucide-react icons
vi.mock('lucide-react', () => ({
  Upload: vi.fn(() => React.createElement('div', { 'data-testid': 'upload-icon' }, 'Upload')),
  File: vi.fn(() => React.createElement('div', { 'data-testid': 'file-icon' }, 'File')),
  X: vi.fn(() => React.createElement('div', { 'data-testid': 'x-icon' }, 'X')),
  Loader2: vi.fn(() => React.createElement('div', { 'data-testid': 'loader-icon' }, 'Loader')),
  Check: vi.fn(() => React.createElement('div', { 'data-testid': 'check-icon' }, 'Check')),
  Circle: vi.fn(() => React.createElement('div', { 'data-testid': 'circle-icon' }, 'Circle')),
  AlertTriangle: vi.fn(() => React.createElement('svg', { 'data-testid': 'alert-triangle-icon' }, 'AlertTriangle')),
  CheckCircle2: vi.fn(() => React.createElement('svg', { 'data-testid': 'check-circle-icon' }, 'CheckCircle2')),
  Clock: vi.fn(() => React.createElement('svg', { 'data-testid': 'clock-icon' }, 'Clock')),
  FileCheck: vi.fn(() => React.createElement('svg', { 'data-testid': 'file-check-icon' }, 'FileCheck')),
  Download: vi.fn(() => React.createElement('svg', { 'data-testid': 'download-icon' }, 'Download')),
  FileText: vi.fn(() => React.createElement('svg', { 'data-testid': 'file-text-icon' }, 'FileText')),
  RefreshCw: vi.fn(() => React.createElement('svg', { 'data-testid': 'refresh-icon' }, 'RefreshCw')),
}));

// Mock Supabase
vi.mock('@supabase/supabase-js', () => ({
  createClient: vi.fn(() => ({
    from: vi.fn(() => ({
      select: vi.fn(() => ({
        eq: vi.fn(() => ({
          single: vi.fn(() => Promise.resolve({ data: null, error: null })),
        })),
        insert: vi.fn(() => Promise.resolve({ data: null, error: null })),
        update: vi.fn(() => Promise.resolve({ data: null, error: null })),
        delete: vi.fn(() => Promise.resolve({ data: null, error: null })),
      })),
    })),
    storage: {
      from: vi.fn(() => ({
        upload: vi.fn(() => Promise.resolve({ data: null, error: null })),
        download: vi.fn(() => Promise.resolve({ data: null, error: null })),
        getPublicUrl: vi.fn(() => ({ data: { publicUrl: '' } })),
      })),
    },
  })),
}));
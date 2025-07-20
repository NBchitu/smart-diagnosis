'use client';

import React from 'react';
import WiFiScanResults from '@/components/wifi/WiFiScanResults';

export default function WiFiScanPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto">
        <WiFiScanResults />
      </div>
    </div>
  );
} 
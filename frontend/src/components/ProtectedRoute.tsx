'use client';

import { useEffect, useState } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { isAuthenticated } from '@/lib/auth';

export default function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const [isChecking, setIsChecking] = useState(true);

  useEffect(() => {
    // Check authentication immediately
    const checkAuth = () => {
      if (!isAuthenticated()) {
        router.replace('/login');
      } else {
        setIsChecking(false);
      }
    };

    checkAuth();
  }, [pathname, router]);

  // Don't render anything until we've checked authentication
  // This prevents flash of content before redirect
  if (isChecking || !isAuthenticated()) {
    return null;
  }

  return <>{children}</>;
}

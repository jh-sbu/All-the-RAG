import { useState, useRef, useEffect } from 'react';
import { Session } from '@supabase/supabase-js';
import { supabase } from '../lib/supabase';
import './ProfileMenu.css';

interface ProfileMenuProps {
  session: Session | null;
  onLoginClick: () => void;
}

const ProfileMenu = ({ session, onLoginClick }: ProfileMenuProps) => {
  const [isOpen, setIsOpen] = useState(false);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setIsOpen(false);
        setShowDeleteConfirm(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleLogout = async () => {
    await supabase.auth.signOut();
    setIsOpen(false);
  };

  const handleDeleteAccount = async () => {
    if (!showDeleteConfirm) {
      setShowDeleteConfirm(true);
      return;
    }

    try {
      // Call your backend API to delete the user account
      // This requires a backend endpoint that deletes the user from Supabase Auth
      const { error } = await supabase.rpc('delete_user');
      if (error) throw error;

      await supabase.auth.signOut();
      setIsOpen(false);
      setShowDeleteConfirm(false);
    } catch (error) {
      console.error('Error deleting account:', error);
      alert('Failed to delete account. Please try again or contact support.');
    }
  };

  const getUserEmail = () => {
    return session?.user?.email || 'User';
  };

  const getInitials = () => {
    const email = getUserEmail();
    return email.charAt(0).toUpperCase();
  };

  return (
    <div className="profile-menu" ref={menuRef}>
      <button
        className="profile-button"
        onClick={() => setIsOpen(!isOpen)}
        aria-label="Profile menu"
      >
        <div className="profile-avatar">
          {session ? getInitials() : '?'}
        </div>
      </button>

      {isOpen && (
        <div className="profile-dropdown">
          {session ? (
            <>
              <div className="profile-header">
                <div className="profile-email">{getUserEmail()}</div>
              </div>
              <div className="profile-divider"></div>
              {/* Placeholder for future Profile option */}
              <button className="profile-menu-item" onClick={handleLogout}>
                Log Out
              </button>
              <div className="profile-divider"></div>
              <button
                className={`profile-menu-item danger ${showDeleteConfirm ? 'confirm' : ''}`}
                onClick={handleDeleteAccount}
              >
                {showDeleteConfirm ? 'Click again to confirm' : 'Delete Account'}
              </button>
            </>
          ) : (
            <button className="profile-menu-item" onClick={() => {
              setIsOpen(false);
              onLoginClick();
            }}>
              Log In
            </button>
          )}
        </div>
      )}
    </div>
  );
};

export default ProfileMenu;

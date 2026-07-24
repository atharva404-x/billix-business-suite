import { useAuth, useUser } from "@clerk/clerk-react";

export function useAuthentication() {
  const { isLoaded: authLoaded, userId, getToken, signOut } = useAuth();
  const { isLoaded: userLoaded, user } = useUser();

  const isLoading = !authLoaded || (userId ? !userLoaded : false);
  const isAuthenticated = !!userId;

  const mappedUser = user
    ? {
        id: user.id,
        firstName: user.firstName,
        lastName: user.lastName,
        email: user.primaryEmailAddress?.emailAddress ?? "",
        avatarUrl: user.imageUrl,
        fullName: user.fullName,
      }
    : null;

  return {
    isLoading,
    isAuthenticated,
    user: mappedUser,
    getToken,
    logout: signOut,
  };
}

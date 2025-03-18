import { useEffect } from "react";
import { axiosInstance, fetchData } from "../api/axiosClient";
import ThemeController from "./ThemeController";

interface AuthStatus {
  is_authenticated: boolean,
  // username: string
}

const Navbar = (
  {
    authStatus, 
    setAuthStatus
  }: 
  {
    authStatus: boolean,
    setAuthStatus: CallableFunction
  }
) => {

  useEffect(() => {
    (async () => {
      const data = await fetchData<AuthStatus>("/github/auth_status")
      const isAuthenticated = Boolean(data['is_authenticated'])
      setAuthStatus(isAuthenticated)
    })();
    

  }, [])

  function handleGithubLogin() {
    const authUrl = axiosInstance.getUri() + "github/auth"
    window.open(authUrl, '_blank')?.focus()
  }
  return (
    <div className="navbar bg-base-100 shadow-sm">


      <div className="navbar-start">
        <a className="btn btn-ghost text-xl">Year in data</a>
      </div>



      <div className="navbar-end flex-none gap-5 p-">
            <ThemeController />
            {authStatus ? 
              <a className="btn">Log out</a>  
              : <a className="btn" onClick={handleGithubLogin}>Dev Login</a>
            }
            
      </div>

    </div>
  );
};

export default Navbar;
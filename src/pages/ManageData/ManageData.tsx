import { useEffect, useState } from "react";
import { axiosInstance, fetchData } from "../../api/axiosClient";
import styles from "./ManageData.module.css"
import { FaGithub } from "react-icons/fa6";


interface auth_status {
  "is_authenticated": string
}

const ManageData = () => {
  const [authStatus, setAuthStatus] = useState(false)

  useEffect(() => {
    (async () => {
      const data = await fetchData<auth_status>("/github/auth_status")
      const isAuthenticated = Boolean(data['is_authenticated'])
      setAuthStatus(isAuthenticated)
    })();
  }, [])

  function handleGithubLogin() {
    const authUrl = axiosInstance.getUri() + "github/auth"
    window.open(authUrl, '_blank')?.focus()
  }

  if (!authStatus) {
    return (
      <div className={styles.pageContainer}>
        <div className={styles.container}>
          <h1>Authenticate with Github</h1>
          <p>
            Authenticate with github first to manage data. (Currently only accessible to devs :P)
          </p>
          <p>  
            Refresh page if you've already logged in.
          </p>
          <button
            className={styles.ghSignInButton}
            onClick={handleGithubLogin}
          >
            <FaGithub />
            Sign in with GitHub
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className={styles.pageContainer}>
      <h1>Manage Data</h1>
      

    </div>
  );
}

export default ManageData;
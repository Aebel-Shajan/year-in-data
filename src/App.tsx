import { useState } from "react";
import Heatmap from "./components/Heatmap/Heatmap";
import Navbar from "./components/Navbar";
import ModalButton from "./components/ModalButton";
import { axiosInstance } from "./api/axiosClient";

const HomePage = () => {
  const [authStatus, setAuthStatus] = useState(false)

  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    if (event.target.files && event.target.files.length > 0) {
      setFile(event.target.files[0]);
    }
  };

  const handleUpload = async (url: string) => {
    if (!file) {
      alert("Please select a file first.");
      return;
    }

    setUploading(true);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await axiosInstance.post(
        url,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        }
      )

      if (response.status == 201) {
        alert("File uploaded successfully!");
        setFile(null);
      } else {
        alert("Failed to upload file.");
      }
    } catch (error) {
      console.error("Error uploading file:", error);
      alert("Error uploading file.");
    } finally {
      setUploading(false);
    }
  };


  return (
    <div className="min-h-screen bg-base-200 max-w-screen overflow-x-hidden">
      <Navbar authStatus={authStatus} setAuthStatus={setAuthStatus} />

      <div className="p-8 min-h-screen w-full flex flex-col items-center gap-5">


        <div className="p-4 bg-base-100 border-base-300 border-2 text-base-content rounded-md  w-fit max-w-full">
          <div className="flex justify-between">

            <h1 className="text-xl font-semibold">
              Reading Activity
            </h1>
            <ModalButton buttonText="upload files" >
              <div className="flex flex-col gap-5">

                <h1 className="font-semibold text-xl">Upload kindle zip</h1>
                <input
                  type="file"
                  className="file-input"
                  accept=".zip"
                  onChange={handleFileChange}
                />
                {file && <p className="text-sm text-gray-600">Selected: {file.name}</p>}
                <button onClick={() => handleUpload("/reading/upload_file")} disabled={uploading || !file} className="btn w-full">
                  {uploading ? "Uploading..." : "Upload File"}
                </button>
              </div>

            </ModalButton>
          </div>
          <div className="p-3 flex justify-center overflow-x-scroll">
            <Heatmap url="/reading/2024" name="reading" />
          </div>
        </div>

        <div className="p-4 bg-base-100 border-base-300 border-2 text-base-content rounded-md  w-fit max-w-full">
          <h1 className="text-xl font-semibold">
            Github Activity
          </h1>
          <div className="p-3 flex justify-center overflow-x-scroll">
            <Heatmap url="/github/2024" name="github" />
          </div>
        </div>


        <div className="p-4 bg-base-100 border-base-300 border-2 text-base-content rounded-md  w-fit max-w-full">
          <div className="flex justify-between" >
            <h1 className="text-xl font-semibold">
              Workout Activity
            </h1>
            <ModalButton buttonText="upload files" >
              <div className="flex flex-col gap-5">

                <h1 className="font-semibold text-xl">Upload strong csv files</h1>
                <input
                  type="file"
                  className="file-input"
                  accept=".csv"
                  onChange={handleFileChange}
                />
                {file && <p className="text-sm text-gray-600">Selected: {file.name}</p>}
                <button onClick={() => handleUpload("/workouts/upload_file")} disabled={uploading || !file} className="btn w-full">
                  {uploading ? "Uploading..." : "Upload File"}
                </button>
              </div>

            </ModalButton>
          </div>

          <div className="p-3 flex justify-center overflow-x-scroll">
            <Heatmap
              url="/workouts/2024"
              name="workouts"
              colorRange={["powderblue", "slateblue"]}
            />
          </div>
        </div>


      </div>

    </div>
  );
};

export default HomePage;

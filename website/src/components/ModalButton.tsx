import { useRef } from "react";

const ModalButton = (
  {
    buttonText,
    children
  }:
  {
    buttonText: string,
    children: React.ReactNode
  }
) => {
  const modalRef = useRef<HTMLDialogElement|null>(null)

  function handleShowModal() {
    if (!modalRef.current) return 
    
    modalRef.current.showModal()

  }

  return (
    <>
      <button className="btn" onClick={handleShowModal}>{buttonText}</button>
      <dialog ref={modalRef} className="modal">
        <div className="modal-box">
          {children}
          <div className="modal-action">
            <form method="dialog">
              {/* if there is a button in form, it will close the modal */}
              <button className="btn">Close</button>
            </form>
          </div>
        </div>
      </dialog>
    </>
  );
}

export default ModalButton;
import styles from "./Modal.module.css"
import { IoMdClose } from "react-icons/io"

interface ModalProps {
  onClose: CallableFunction,
  children: React.ReactNode
}

const Modal = (
  {
    onClose,
    children
  }: ModalProps
) => {
  return (
    <div className={styles.modal}>
      <button
        className={styles.closeButton}
        onClick={() => onClose()}
      >
        <IoMdClose />
      </button>
      {children}
    </div>
  );
}

export default Modal;
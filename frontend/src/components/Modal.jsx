import React from 'react';

export default function Modal({ isOpen, title, onClose, children }) {
  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2 style={{ fontSize: '1.2rem', fontWeight: 700 }}>{title}</h2>
          <button className="modal-close" onClick={onClose}>&times;</button>
        </div>
        <div>
          {children}
        </div>
      </div>
    </div>
  );
}

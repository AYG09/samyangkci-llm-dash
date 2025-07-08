// clipboard.js: Dash에서 프롬프트 복사 기능을 위한 JS
// textarea를 querySelector로 직접 찾고, readonly 일시 해제 후 복사

console.log('[clipboard.js] loaded');
document.addEventListener('DOMContentLoaded', function() {
  document.addEventListener('click', function(e) {
    if (e.target && e.target.id === 'copy-btn') {
      console.log('[복사] copy-btn 클릭');
      const wrapper = document.getElementById('prompt-generated-prompt-area-wrapper');
      console.log('[복사] wrapper:', wrapper);
      const textarea = wrapper ? wrapper.querySelector('textarea') : null;
      console.log('[복사] textarea:', textarea);
      if (textarea) {
        const wasReadOnly = textarea.readOnly;
        textarea.readOnly = false;
        textarea.focus();
        textarea.select();
        const text = textarea.value;
        console.log('[복사] 복사할 텍스트:', text);
        // Clipboard API 우선
        if (navigator.clipboard && window.isSecureContext) {
          navigator.clipboard.writeText(text).then(function() {
            console.log('[복사] Clipboard API 성공');
            showCopySuccess(textarea);
            textarea.readOnly = wasReadOnly;
          }, function(err) {
            console.log('[복사] Clipboard API 실패', err);
            fallbackCopy(textarea, wasReadOnly);
          });
        } else {
          console.log('[복사] Clipboard API 미지원, fallbackCopy 시도');
          fallbackCopy(textarea, wasReadOnly);
        }
      } else {
        console.log('[복사] textarea를 찾지 못함');
      }
    }
  });
  function fallbackCopy(textarea, wasReadOnly) {
    try {
      const successful = document.execCommand('copy');
      console.log('[복사] execCommand copy 결과:', successful);
      if (successful) {
        showCopySuccess(textarea);
      }
    } catch (err) {
      alert('복사 실패: ' + err);
      console.log('[복사] execCommand copy 에러:', err);
    }
    textarea.readOnly = wasReadOnly;
  }
  function showCopySuccess(textarea) {
    const msg = document.getElementById('copy-success-msg');
    if (msg) {
      msg.textContent = '복사 완료!';
      setTimeout(() => { msg.textContent = ''; }, 1500);
    }
    textarea.classList.add('balloon');
    setTimeout(() => { textarea.classList.remove('balloon'); }, 800);
    console.log('[복사] 복사 성공 애니메이션/메시지 표시');
  }
});

const CONFIG = {
  labelName: 'SF-Weekly-Reports',
  folderId: '1FX8qdAW7K4qzLledkkugbRr0a8oSXv3c',
  lookbackDays: 14,
  subjectKeywords: ['Closed', 'Transferred'], 
  processedPropKey: 'processed_ids',
  debugMode: true  // Set to true to allow duplicates during testing
};

function saveSalesforceAttachments() {
  const props = PropertiesService.getScriptProperties();
  
  // Skip deduplication if in debug mode
  let processed;
  if (CONFIG.debugMode) {
    processed = new Set();
    Logger.log('Debug mode enabled - duplicates will be allowed');
  } else {
    const raw = props.getProperty(CONFIG.processedPropKey);
    processed = new Set(Array.isArray(JSON.parse(raw || '[]')) ? JSON.parse(raw) : []);
  }

  const folder = DriveApp.getFolderById(CONFIG.folderId);
  const query = `label:${CONFIG.labelName} newer_than:${CONFIG.lookbackDays}d`;
  const threads = GmailApp.search(query, 0, 200);

  let processedList = Array.from(processed);
  let savedCount = 0;

  threads.forEach(thread => {
    const msgs = thread.getMessages();
    if (!msgs || msgs.length === 0) return;
    
    msgs.forEach(msg => {
      const msgId = msg.getId();
      
      // Skip deduplication check in debug mode
      if (!CONFIG.debugMode && processed.has(msgId)) return;

      const attachments = msg.getAttachments({includeInlineImages: false, includeAttachments: true});
      if (!attachments || attachments.length === 0) return;
      
      // Get email subject to extract report type
      const subject = msg.getSubject() || '';
      
      // Check if subject contains any of the required keywords
      const subjectMatches = CONFIG.subjectKeywords.length === 0 || 
                           CONFIG.subjectKeywords.some(k => subject.toLowerCase().includes(k.toLowerCase()));
      
      if (!subjectMatches) {
        Logger.log('Subject does not match keywords, skipping: ' + subject);
        return;
      }
      
      let reportType = 'report';
      
      // Parse report name from subject - check for pattern in parentheses first
      let match = subject.match(/Report results \((.+?)\)/i);
      if (match && match[1]) {
        const reportName = match[1].toLowerCase();
        
        if (reportName.includes('transfer')) {
          reportType = 'transferred';
        } else if (reportName.includes('close')) {
          reportType = 'closed';
        }
      } else {
        // If no parentheses pattern, check the subject line directly
        const subjectLower = subject.toLowerCase();
        
        if (subjectLower.includes('transfer')) {
          reportType = 'transferred';
        } else if (subjectLower.includes('close')) {
          reportType = 'closed';
        }
      }

      attachments.forEach(att => {
        const name = (att.getName() || '').toLowerCase();
        const isCsv = name.endsWith('.csv') || att.getContentType().includes('csv');
        if (!isCsv) return;

        const dateStr = Utilities.formatDate(msg.getDate(), Session.getScriptTimeZone(), 'yyyy-MM-dd');
        const finalName = dateStr + '_' + reportType + '_report.csv';

        folder.createFile(att.copyBlob().setName(finalName));
        savedCount++;
      });

      // Only add to processed list if not in debug mode
      if (!CONFIG.debugMode) {
        processed.add(msgId);
        processedList.push(msgId);
      }
    });
  });

  // Only save processed IDs if not in debug mode
  if (!CONFIG.debugMode) {
    if (processedList.length > 5000) {
      processedList = processedList.slice(processedList.length - 5000);
    }
    props.setProperty(CONFIG.processedPropKey, JSON.stringify(processedList));
  }

  Logger.log('Saved ' + savedCount + ' attachment(s) to Drive folder');
}

function resetProcessedIds() {
  const props = PropertiesService.getScriptProperties();
  props.deleteProperty(CONFIG.processedPropKey);
  Logger.log('Cleared processed IDs');
}
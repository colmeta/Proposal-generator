# Troubleshooting Guide

This guide helps you resolve common issues with the Proposal Generator.

## Common Issues

### API Connection Problems

#### Issue: Cannot Connect to API
**Symptoms**:
- Error message: "Cannot connect to API"
- Health check shows unhealthy
- Requests timeout

**Solutions**:
1. **Check API Status**:
   - Verify backend API is running
   - Check API URL in settings
   - Test API endpoint directly

2. **Network Issues**:
   - Check internet connection
   - Verify firewall settings
   - Test with different network

3. **Configuration**:
   - Verify API base URL
   - Check port number
   - Ensure CORS is enabled

#### Issue: API Timeout
**Symptoms**:
- Requests take too long
- Timeout errors
- Slow responses

**Solutions**:
1. **Increase Timeout**:
   - Go to Settings > LLM Provider
   - Increase request timeout
   - Save settings

2. **Check Network**:
   - Test connection speed
   - Check for network issues
   - Try different network

3. **Optimize Requests**:
   - Reduce max tokens
   - Simplify requests
   - Use faster models

### Proposal Creation Issues

#### Issue: Form Validation Errors
**Symptoms**:
- Cannot submit proposal
- Red error messages
- Missing field warnings

**Solutions**:
1. **Check Required Fields**:
   - Review form for required fields (marked with *)
   - Fill in all required information
   - Verify field formats

2. **Validate Input**:
   - Check email format
   - Verify URL format
   - Ensure budget is numeric

3. **Clear Errors**:
   - Fix validation errors
   - Refresh page if needed
   - Try again

#### Issue: File Upload Fails
**Symptoms**:
- Files don't upload
- Upload errors
- Files rejected

**Solutions**:
1. **Check File Type**:
   - Ensure file type is supported (PDF, DOCX, TXT)
   - Convert if needed
   - Check file extension

2. **Check File Size**:
   - Ensure file is under 10MB
   - Compress if needed
   - Split large files

3. **Check Permissions**:
   - Verify file is not locked
   - Check file permissions
   - Try different file

### Job Processing Issues

#### Issue: Job Stuck in Processing
**Symptoms**:
- Job status shows "Processing" for long time
- No progress updates
- Job doesn't complete

**Solutions**:
1. **Check Job Status**:
   - View job details
   - Check for errors
   - Review task status

2. **Wait Longer**:
   - Complex proposals take time
   - Check estimated completion
   - Be patient

3. **Restart Job**:
   - Cancel stuck job
   - Create new job
   - Monitor progress

#### Issue: Job Fails
**Symptoms**:
- Job status shows "Failed"
- Error messages displayed
- No document generated

**Solutions**:
1. **Check Error Message**:
   - Read error details
   - Identify cause
   - Check logs

2. **Common Causes**:
   - API key issues
   - Invalid input data
   - Network problems
   - Rate limiting

3. **Fix and Retry**:
   - Address root cause
   - Update proposal if needed
   - Create new job

### Document Issues

#### Issue: Document Not Generated
**Symptoms**:
- Job completes but no document
- Document missing
- Cannot view document

**Solutions**:
1. **Check Job Status**:
   - Verify job completed successfully
   - Check for errors
   - Review job logs

2. **Check Storage**:
   - Verify storage configuration
   - Check storage permissions
   - Review storage logs

3. **Regenerate**:
   - Create new job
   - Monitor progress
   - Check again

#### Issue: Document Format Issues
**Symptoms**:
- Formatting problems
- Missing sections
- Incorrect layout

**Solutions**:
1. **Check Input**:
   - Review proposal data
   - Verify all sections filled
   - Check for special characters

2. **Try Different Format**:
   - Download as PDF
   - Download as DOCX
   - Compare formats

3. **Regenerate**:
   - Make corrections
   - Resubmit proposal
   - Check new document

### Quality Issues

#### Issue: Low Quality Score
**Symptoms**:
- Quality score below threshold
- Document rejected
- Auto-revision triggered

**Solutions**:
1. **Improve Input**:
   - Add more detail
   - Clarify objectives
   - Enhance descriptions

2. **Adjust Settings**:
   - Lower quality threshold (temporary)
   - Enable auto-revision
   - Use better model

3. **Review Output**:
   - Check generated content
   - Identify issues
   - Make improvements

### Authentication Issues

#### Issue: API Key Not Working
**Symptoms**:
- Authentication errors
- "Invalid API key" messages
- Requests rejected

**Solutions**:
1. **Verify Key**:
   - Check key is correct
   - Ensure no extra spaces
   - Verify key is active

2. **Check Provider**:
   - Verify account status
   - Check billing
   - Review usage limits

3. **Regenerate Key**:
   - Create new API key
   - Update in settings
   - Test again

### Performance Issues

#### Issue: Slow Performance
**Symptoms**:
- Slow page loads
- Delayed responses
- Timeout errors

**Solutions**:
1. **Check System**:
   - Verify system resources
   - Check network speed
   - Review server load

2. **Optimize Settings**:
   - Reduce max tokens
   - Use faster models
   - Disable unnecessary features

3. **Clear Cache**:
   - Clear browser cache
   - Clear session data
   - Refresh page

## Error Messages

### Common Error Messages

#### "API Connection Failed"
- **Cause**: Cannot reach API server
- **Solution**: Check API status and URL

#### "Invalid API Key"
- **Cause**: API key incorrect or expired
- **Solution**: Verify and update API key

#### "Rate Limit Exceeded"
- **Cause**: Too many requests
- **Solution**: Wait and retry, or upgrade plan

#### "Validation Error"
- **Cause**: Invalid input data
- **Solution**: Check and fix form data

#### "Job Failed"
- **Cause**: Processing error
- **Solution**: Check error details and retry

#### "Document Not Found"
- **Cause**: Document not generated or deleted
- **Solution**: Regenerate document

## Getting Help

### Self-Help Resources
1. **Documentation**: Review user guides
2. **FAQ**: Check frequently asked questions
3. **Search**: Search documentation
4. **Examples**: Review code examples

### Support Channels
1. **In-App Help**: Use help system
2. **Documentation**: Read guides
3. **GitHub Issues**: Report bugs
4. **Email Support**: Contact support team

### Reporting Issues

When reporting issues, include:
- **Description**: What happened
- **Steps**: How to reproduce
- **Expected**: What should happen
- **Actual**: What actually happened
- **Environment**: System details
- **Logs**: Error messages and logs

## Prevention Tips

### Best Practices
1. **Keep Updated**: Use latest version
2. **Backup Data**: Regular backups
3. **Monitor Status**: Check system health
4. **Test Changes**: Test before production
5. **Read Documentation**: Stay informed

### Regular Maintenance
1. **Update Dependencies**: Keep packages updated
2. **Check Logs**: Review regularly
3. **Monitor Usage**: Track API usage
4. **Review Settings**: Verify configuration
5. **Test Features**: Regular testing

## Advanced Troubleshooting

### Logs and Debugging
- **Enable Debug Mode**: For detailed logs
- **Check Log Files**: Review error logs
- **API Logs**: Check API server logs
- **Browser Console**: Check browser errors

### System Diagnostics
- **Health Check**: Verify system health
- **Resource Usage**: Check CPU, memory
- **Network Status**: Test connectivity
- **Database Status**: Verify database

### Recovery Procedures
- **Restore Backup**: If data lost
- **Reset Settings**: If configuration corrupted
- **Reinstall**: Last resort option
- **Contact Support**: For critical issues

## Next Steps

- Review [Getting Started Guide](getting_started.md)
- Check [FAQ](../faq.md)
- Explore [Best Practices](../guides/best_practices.md)



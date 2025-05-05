from django.db import migrations
from django.utils import timezone

def create_legal_pages(apps, schema_editor):
    """Create initial legal pages."""
    LegalPage = apps.get_model('jobs', 'LegalPage')
    
    # Terms and Conditions
    terms_content = """
<h1>1. Introduction</h1>
<p>Welcome to SearchFind. These Terms and Conditions govern your use of our website and services. By accessing or using SearchFind, you agree to be bound by these Terms. If you disagree with any part of the terms, you may not access the service.</p>

<h2>2. Definitions</h2>
<ul>
    <li><strong>"Service"</strong> refers to the SearchFind website and platform.</li>
    <li><strong>"User"</strong> refers to individuals who access or use our Service.</li>
    <li><strong>"Job Seeker"</strong> refers to users who use our Service to search for and apply to jobs.</li>
    <li><strong>"Employer"</strong> refers to users who use our Service to post job listings and recruit candidates.</li>
    <li><strong>"Content"</strong> refers to text, images, videos, and other materials that appear on our Service.</li>
</ul>

<h2>3. User Accounts</h2>
<p>When you create an account with us, you must provide accurate, complete, and up-to-date information. You are responsible for safeguarding the password and for all activities that occur under your account. You agree to notify us immediately of any unauthorized use of your account.</p>

<h2>4. Job Listings and Applications</h2>
<p>Employers are responsible for the accuracy of their job listings. SearchFind does not guarantee the validity of job listings or the qualifications of applicants. Job seekers are responsible for the accuracy of their applications and resumes.</p>

<h2>5. Subscription Services</h2>
<p>Some features of our Service require a paid subscription. By subscribing to a premium plan, you agree to pay the fees as described at the time of purchase. Subscription fees are non-refundable except as required by law or as explicitly stated in these Terms.</p>

<h2>6. Payment Terms</h2>
<p>We use third-party payment processors to bill you through a payment account linked to your account. The processing of payments will be subject to the terms, conditions, and privacy policies of the payment processor in addition to these Terms.</p>

<h2>7. Content and Conduct</h2>
<p>You retain all rights to any content you submit, post, or display on or through the Service. By submitting content to SearchFind, you grant us a worldwide, non-exclusive, royalty-free license to use, reproduce, modify, adapt, publish, and display such content.</p>
<p>You agree not to post content that:</p>
<ul>
    <li>Is unlawful, harmful, threatening, abusive, harassing, defamatory, or invasive of another's privacy</li>
    <li>Infringes any patent, trademark, trade secret, copyright, or other intellectual property rights</li>
    <li>Contains software viruses or any other code designed to interrupt, destroy, or limit the functionality of any computer software or hardware</li>
    <li>Is false, inaccurate, or misleading</li>
</ul>

<h2>8. Termination</h2>
<p>We may terminate or suspend your account immediately, without prior notice or liability, for any reason, including without limitation if you breach the Terms. Upon termination, your right to use the Service will immediately cease.</p>

<h2>9. Limitation of Liability</h2>
<p>In no event shall SearchFind, its directors, employees, partners, agents, suppliers, or affiliates be liable for any indirect, incidental, special, consequential, or punitive damages, including without limitation, loss of profits, data, use, goodwill, or other intangible losses, resulting from your access to or use of or inability to access or use the Service.</p>

<h2>10. Changes to Terms</h2>
<p>We reserve the right, at our sole discretion, to modify or replace these Terms at any time. If a revision is material, we will try to provide at least 30 days' notice prior to any new terms taking effect. What constitutes a material change will be determined at our sole discretion.</p>

<h2>11. Contact Us</h2>
<p>If you have any questions about these Terms, please contact us at <a href="mailto:info@searchfind.com">info@searchfind.com</a>.</p>
"""

    # Privacy Policy
    privacy_content = """
<h1>1. Introduction</h1>
<p>At SearchFind, we respect your privacy and are committed to protecting your personal data. This Privacy Policy explains how we collect, use, disclose, and safeguard your information when you use our website and services.</p>

<h2>2. Information We Collect</h2>
<p>We collect several types of information from and about users of our website, including:</p>
<ul>
    <li><strong>Personal Information:</strong> Name, email address, phone number, postal address, and professional information such as work history, education, and skills.</li>
    <li><strong>Account Information:</strong> Username, password, and account preferences.</li>
    <li><strong>Profile Information:</strong> Resume, profile picture, and other information you choose to include in your profile.</li>
    <li><strong>Usage Data:</strong> Information about how you use our website, including browsing patterns, search queries, and interaction with job listings.</li>
    <li><strong>Technical Data:</strong> IP address, browser type and version, device information, and other technology identifiers.</li>
</ul>

<h2>3. How We Collect Your Information</h2>
<p>We collect information through:</p>
<ul>
    <li>Direct interactions when you create an account, upload a resume, apply for jobs, or contact us.</li>
    <li>Automated technologies such as cookies and similar tracking technologies.</li>
    <li>Third parties such as social media platforms if you choose to link your account.</li>
</ul>

<h2>4. How We Use Your Information</h2>
<p>We use your information to:</p>
<ul>
    <li>Provide and maintain our services</li>
    <li>Match job seekers with relevant job opportunities</li>
    <li>Process job applications</li>
    <li>Communicate with you about our services</li>
    <li>Improve and personalize your experience</li>
    <li>Analyze usage patterns and trends</li>
    <li>Prevent fraud and enhance security</li>
</ul>

<h2>5. Disclosure of Your Information</h2>
<p>We may share your personal information with:</p>
<ul>
    <li><strong>Employers:</strong> When you apply for jobs, your application and profile information will be shared with the employer.</li>
    <li><strong>Service Providers:</strong> Third-party vendors who perform services on our behalf, such as payment processing and data analysis.</li>
    <li><strong>Legal Requirements:</strong> When required by law or to protect our rights.</li>
</ul>

<h2>6. Data Security</h2>
<p>We have implemented appropriate security measures to prevent your personal data from being accidentally lost, used, or accessed in an unauthorized way. We limit access to your personal data to employees and third parties who have a business need to know.</p>

<h2>7. Your Data Protection Rights</h2>
<p>Depending on your location, you may have the following rights:</p>
<ul>
    <li>The right to access your personal data</li>
    <li>The right to correct inaccurate personal data</li>
    <li>The right to request deletion of your personal data</li>
    <li>The right to restrict processing of your personal data</li>
    <li>The right to data portability</li>
    <li>The right to object to processing of your personal data</li>
</ul>

<h2>8. Cookies and Tracking Technologies</h2>
<p>We use cookies and similar tracking technologies to track activity on our website and store certain information. You can instruct your browser to refuse all cookies or to indicate when a cookie is being sent. However, if you do not accept cookies, you may not be able to use some portions of our Service.</p>

<h2>9. Children's Privacy</h2>
<p>Our Service is not intended for use by children under the age of 16. We do not knowingly collect personally identifiable information from children under 16. If you are a parent or guardian and you are aware that your child has provided us with personal data, please contact us.</p>

<h2>10. Changes to This Privacy Policy</h2>
<p>We may update our Privacy Policy from time to time. We will notify you of any changes by posting the new Privacy Policy on this page and updating the "Last updated" date.</p>

<h2>11. Contact Us</h2>
<p>If you have any questions about this Privacy Policy, please contact us at <a href="mailto:privacy@searchfind.com">privacy@searchfind.com</a>.</p>
"""

    # Cookie Policy
    cookies_content = """
<h1>1. What Are Cookies</h1>
<p>Cookies are small text files that are placed on your computer or mobile device when you visit a website. They are widely used to make websites work more efficiently and provide information to the website owners. Cookies help us improve your experience on our website and deliver personalized content.</p>

<h2>2. How We Use Cookies</h2>
<p>We use cookies for various purposes, including:</p>
<ul>
    <li><strong>Essential Cookies:</strong> These cookies are necessary for the website to function properly. They enable core functionality such as security, network management, and account access.</li>
    <li><strong>Preference Cookies:</strong> These cookies allow us to remember choices you make and provide enhanced, personalized features. They may be set by us or by third-party providers whose services we have added to our pages.</li>
    <li><strong>Analytics Cookies:</strong> These cookies help us understand how visitors interact with our website by collecting and reporting information anonymously. They help us improve the way our website works.</li>
    <li><strong>Marketing Cookies:</strong> These cookies are used to track visitors across websites. They are set to display targeted advertisements based on your interests and online behavior.</li>
    <li><strong>Session Cookies:</strong> These are temporary cookies that are deleted when you close your browser. They help us track your movements from page to page so you don't have to provide the same information repeatedly.</li>
</ul>

<h2>3. Types of Cookies We Use</h2>
<h3>First-Party Cookies</h3>
<p>These are cookies that are set by our website directly. They are used to maintain your session and remember your preferences.</p>

<h3>Third-Party Cookies</h3>
<p>These are cookies set by our partners and service providers. They may include:</p>
<ul>
    <li>Analytics providers (like Google Analytics)</li>
    <li>Advertising networks</li>
    <li>Social media platforms</li>
    <li>Payment processors</li>
</ul>

<h2>4. Cookie Management</h2>
<p>Most web browsers allow you to control cookies through their settings. You can:</p>
<ul>
    <li>Delete cookies from your device</li>
    <li>Block cookies by activating the setting on your browser that allows you to refuse all or some cookies</li>
    <li>Set your browser to notify you when you receive a cookie</li>
</ul>

<p>Please note that if you choose to block or delete cookies, you may not be able to access certain areas or features of our website, and some services may not function properly.</p>

<h3>How to Manage Cookies in Different Browsers</h3>
<ul>
    <li><strong>Chrome:</strong> Settings → Privacy and security → Cookies and other site data</li>
    <li><strong>Firefox:</strong> Options → Privacy & Security → Cookies and Site Data</li>
    <li><strong>Safari:</strong> Preferences → Privacy → Cookies and website data</li>
    <li><strong>Edge:</strong> Settings → Site permissions → Cookies and site data</li>
</ul>

<h2>5. Changes to Our Cookie Policy</h2>
<p>We may update our Cookie Policy from time to time. Any changes will be posted on this page with an updated revision date. We encourage you to review this Cookie Policy periodically to stay informed about how we use cookies.</p>

<h2>6. Contact Us</h2>
<p>If you have any questions about our Cookie Policy, please contact us at <a href="mailto:privacy@searchfind.com">privacy@searchfind.com</a>.</p>
"""

    # Create the legal pages
    LegalPage.objects.create(
        title="Terms and Conditions",
        slug="terms-and-conditions",
        page_type="terms",
        content=terms_content,
        is_active=True,
        created_at=timezone.now(),
        updated_at=timezone.now()
    )
    
    LegalPage.objects.create(
        title="Privacy Policy",
        slug="privacy-policy",
        page_type="privacy",
        content=privacy_content,
        is_active=True,
        created_at=timezone.now(),
        updated_at=timezone.now()
    )
    
    LegalPage.objects.create(
        title="Cookie Policy",
        slug="cookie-policy",
        page_type="cookies",
        content=cookies_content,
        is_active=True,
        created_at=timezone.now(),
        updated_at=timezone.now()
    )


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_legal_pages),
    ]

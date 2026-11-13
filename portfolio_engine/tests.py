from django.contrib.auth.hashers import check_password, make_password
from django.test import TestCase
from django.urls import reverse

from .models import ContactMessage, NetworkRegistryTicket


class RegistryAccessTests(TestCase):
    def sign_in_contact_user(self):
        ticket = NetworkRegistryTicket.objects.create(
            full_identity='Test Sender',
            secure_email='account@example.com',
            associated_organization='Independent Node',
            collaboration_scope='Contact test',
            username='contacttest',
        )
        session = self.client.session
        session['ticket_id'] = ticket.pk
        session.save()

    def test_guest_contact_submission_requires_sign_in(self):
        response = self.client.post(reverse('contact'), {
            'name': 'Test Sender',
            'email': 'sender@gmail.com',
            'message': 'Hello',
        })

        self.assertRedirects(
            response,
            f"{reverse('login')}?next=%2Fvault%2F%23contact",
            fetch_redirect_response=False,
        )
        self.assertFalse(ContactMessage.objects.exists())

    def test_guest_sms_request_requires_sign_in(self):
        response = self.client.get(reverse('send_sms'))

        self.assertRedirects(
            response,
            f"{reverse('login')}?next=%2Fsend-sms%2F",
            fetch_redirect_response=False,
        )

    def test_signed_in_sms_request_shows_open_sms_action(self):
        self.sign_in_contact_user()

        response = self.client.get(reverse('send_sms'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'sms:+254791209899')

    def test_contact_form_rejects_non_gmail_addresses(self):
        self.sign_in_contact_user()
        response = self.client.post(reverse('contact'), {
            'name': 'Test Sender',
            'email': 'sender@example.com',
            'message': 'Hello',
        })

        self.assertRedirects(response, '/vault/#contact', fetch_redirect_response=False)
        self.assertFalse(ContactMessage.objects.exists())

    def test_contact_form_saves_gmail_address(self):
        self.sign_in_contact_user()
        response = self.client.post(reverse('contact'), {
            'name': 'Test Sender',
            'email': 'sender@gmail.com',
            'message': 'Hello',
        })

        self.assertRedirects(response, '/vault/#contact', fetch_redirect_response=False)
        self.assertTrue(ContactMessage.objects.filter(email='sender@gmail.com').exists())

    def test_navigation_marks_current_page(self):
        response = self.client.get(reverse('index'))

        self.assertContains(response, 'aria-current="page">System Status')

    def test_guest_vault_request_redirects_to_login_with_return_url(self):
        response = self.client.get(reverse('vault'))

        self.assertRedirects(response, f"{reverse('login')}?next=%2Fvault%2F", fetch_redirect_response=False)

    def test_registration_hashes_password_and_login_returns_to_vault(self):
        registration_response = self.client.post(reverse('registry'), {
            'identity': 'Test Developer',
            'email': 'developer@example.com',
            'org': 'Independent Node',
            'scope': 'Test projects',
            'specialization': 'backend',
            'username': 'testdeveloper',
            'password': 'long-test-password',
            'password_confirm': 'long-test-password',
        })

        self.assertRedirects(registration_response, reverse('dashboard'), fetch_redirect_response=False)
        ticket = NetworkRegistryTicket.objects.get(username='testdeveloper')
        self.assertNotEqual(ticket.password, 'long-test-password')
        self.assertTrue(check_password('long-test-password', ticket.password))

        # Clear session to verify independent login flow
        self.client.session.clear()
        login_response = self.client.post(reverse('login'), {
            'username': 'testdeveloper',
            'password': 'long-test-password',
            'next': reverse('vault'),
        })

        self.assertRedirects(login_response, reverse('vault'), fetch_redirect_response=False)
        vault_response = self.client.get(reverse('vault'))
        self.assertEqual(vault_response.status_code, 200)
        self.assertContains(vault_response, 'Developer Training')

    def test_email_login_upgrades_legacy_plaintext_password(self):
        ticket = NetworkRegistryTicket.objects.create(
            full_identity='Legacy Developer',
            secure_email='legacy@example.com',
            associated_organization='Independent Node',
            collaboration_scope='Legacy account',
            specialization='backend',
            username='legacydeveloper',
            password='legacy-password',
        )

        response = self.client.post(reverse('login'), {
            'username': ticket.secure_email,
            'password': 'legacy-password',
        })

        self.assertRedirects(response, reverse('dashboard'), fetch_redirect_response=False)
        ticket.refresh_from_db()
        self.assertTrue(check_password('legacy-password', ticket.password))
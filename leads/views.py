from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import reverse
from django.views import generic
from django.core.mail import send_mail
from .models import Lead, Agent
from .forms import LeadForm, LeadModelForm, CustomUserCreationForm
from agents.mixins import OrganiserAndLoginRequiredMixin


class SignupView(generic.CreateView):
    template_name = "registration/signup.html"
    form_class =  CustomUserCreationForm

    def get_success_url(self):
        return reverse("login")


class LandingPageView(generic.TemplateView):
    template_name = "landing.html"


class LeadListView(LoginRequiredMixin, generic.ListView):
    template_name = "leads/leads_list.html"
    context_object_name = "leads"

    def get_queryset(self):
        user = self.request.user

        if user.is_organiser:
            queryset = Lead.objects.filter(organization=user.userprofile, agent__isnull=False)
        else:
            queryset = Lead.objects.filter(organization=user.userprofile, agent__isnull=False)
            queryset = queryset.filter(agent__user=user)
        return queryset

    def get_context_data(self, **kwargs):
        user = self.request.user
        context = super(LeadListView, self).get_context_data(**kwargs)

        if user.is_organiser:
            queryset = Lead.objects.filter(organization=user.userprofile, agent__isnull=True)
            context.update({
                "unassigned_leads": queryset
            })

        return context


class LeadDetailView(LoginRequiredMixin, generic.DetailView):
    template_name = "leads/lead_detail.html"
    context_object_name = "lead"

    def get_queryset(self):
        user = self.request.user

        if user.is_organiser:
            queryset = Lead.objects.filter(organization=user.userprofile)
        else:
            queryset = Lead.objects.filter(organization=user.agent.organization)
            queryset = queryset.filter(agent__user=user)


class LeadCreateView(OrganiserAndLoginRequiredMixin, generic.CreateView):
    template_name = "leads/lead_create.html"
    form_class = LeadModelForm

    def get_success_url(self):
        return reverse("leads:lead-list")

    def form_valid(self, form):
        lead = form.save(commit=False)
        lead.organization = self.request.user.userprofile

        send_mail(
            subject="A lead has been created",
            message="Go to the site to see the new lead",
            from_email="test@test.com",
            recipient_list=["test2@test.com"]
        )
        return super(LeadCreateView, self).form_valid(form)


class LeadUpdateView(OrganiserAndLoginRequiredMixin, generic.UpdateView):
    template_name = "leads/lead_update.html"
    form_class = LeadModelForm

    def get_queryset(self):
        user = self.request.user
        queryset = Lead.objects.filter(organization=user.userprofile)

    def get_success_url(self):
        return reverse("leads:lead-list")


class LeadDeleteView(OrganiserAndLoginRequiredMixin, generic.DeleteView):
    template_name = "leads/lead_delete.html"

    def get_queryset(self):
        user = self.request.user
        queryset = Lead.objects.filter(organization=user.userprofile)

    def get_success_url(self):
        return reverse("leads:lead-list")


